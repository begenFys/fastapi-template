"""Базовый репозиторий sqlalchemy."""

# ruff: noqa: D102
# mypy: disable-error-code="type-arg,arg-type,assignment,call-overload,call-arg,attr-defined"
# TODO: typing...
from collections.abc import Sequence
from datetime import datetime
from typing import (
    Any,
)

from sqlalchemy import (
    BinaryExpression,
    Select,
    and_,
    delete,
    func,
    not_,
    or_,
    update,
)
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import aliased, load_only
from sqlalchemy.orm.relationships import RelationshipDirection
from sqlalchemy.sql.expression import select

from src.core.database.base import Base
from src.core.exception.base import (
    BadRequestException,
)
from src.core.exception.database import FieldException
from src.core.helper.scheme.request.filter import (
    FilterParam,
    FilterRequest,
)
from src.core.helper.type.filter import FilterType, OperatorType
from src.core.helper.type.sort import SortType
from src.core.repository import BaseRepository


class SQLAlchemyRepository[
    ModelType: Base,
    SessionType: AsyncSession,
    QueryType: Select,
](
    BaseRepository,
):
    """Базовый класс для репозиториев данных sqlalchemy."""

    model_class: type[ModelType]
    session: type[SessionType]

    async def _create(self, model: ModelType) -> None:
        self.session.add(model)

    async def _update(
        self,
        model: ModelType,
    ) -> None:
        await self.session.flush()

    async def _delete(self, model: ModelType) -> None:
        await self.session.delete(model)

    async def update_by_filters(
        self,
        filter_request: FilterRequest,
        attributes: dict[str, Any],
    ) -> list[ModelType]:
        conditions: list[BinaryExpression] = []
        for param in filter_request.filters:
            self._validate_params(param.field)
            conditions.append(
                self._get_by(
                    field=param.field,
                    value=param.value,
                    operator=param.operator,
                ),
            )

        stmt = (
            update(self.model_class)
            .where(
                and_(*conditions)
                if filter_request.type == FilterType.AND
                else or_(*conditions),
            )
            .values(**attributes)
            .returning(self.model_class)
        )

        select_stmt = self._query().from_statement(stmt)

        return await self._all(select_stmt)

    async def delete_by_filters(
        self,
        filter_request: FilterRequest,
    ) -> list[ModelType]:
        conditions: list[BinaryExpression] = []
        for param in filter_request.filters:
            self._validate_params(param.field)
            conditions.append(
                self._get_by(param.field, param.value, param.operator),
            )

        stmt = (
            delete(self.model_class)
            .where(
                and_(*conditions)
                if filter_request.type == FilterType.AND
                else or_(*conditions),
            )
            .returning(self.model_class)
        )

        select_stmt = self._query().from_statement(stmt)

        return await self._all(select_stmt)

    async def get_columns_unique_values(
        self,
        filter_request: FilterRequest | None = None,
        sort_type: SortType | None = SortType.asc,
        _depth: int = 0,
        _max_depth: int = 1,
    ) -> dict[str, list[Any]]:
        query = self._query()
        if filter_request is not None and len(filter_request.filters) > 0:
            for param in filter_request.filters:
                # query = self._maybe_join(query=query, field=param.field)
                self._validate_params(param.field)
            query = self._filter(query=query, filter_request=filter_request)

        unique_values = {}
        for field in self.model_class.__mapper__.columns.keys():
            atr = getattr(self.model_class, field)

            if sort_type == SortType.desc:
                distinct_query = (
                    query.with_only_columns(
                        atr,
                    )
                    .distinct()
                    .order_by(atr.desc())
                )
            else:
                distinct_query = (
                    query.with_only_columns(
                        atr,
                    )
                    .distinct()
                    .order_by(atr.asc())
                )

            result = await self.session.execute(distinct_query)
            unique_values[field] = [row[0] for row in result.fetchall()]

        # обработка связных полей
        if _depth < _max_depth:
            for (
                sub_model_name,
                sub_model,
            ) in self.model_class.__mapper__.relationships.items():
                if sub_model.direction == RelationshipDirection.MANYTOONE:
                    sub_repository: SQLAlchemyRepository = SQLAlchemyRepository(
                        model=sub_model.entity.class_,
                        db_session=self.session,
                    )
                    linked_model_foreign_key = next(
                        iter(sub_model.local_columns),
                    ).key
                    linked_model_ids = unique_values.get(
                        linked_model_foreign_key,
                    )
                    if linked_model_ids is None:
                        continue

                    sub_filter_request = FilterRequest(
                        filters=[
                            FilterParam(
                                field=next(
                                    iter(
                                        next(
                                            iter(sub_model.local_columns),
                                        ).foreign_keys,
                                    ),
                                ).column.key,
                                value=linked_model_ids,
                                operator=OperatorType.IN,
                            ),
                        ],
                    )
                    sub_unique_values = (
                        await sub_repository.get_columns_unique_values(
                            filter_request=sub_filter_request,
                            _depth=_depth + 1,
                            _max_depth=_max_depth,
                        )
                    )
                    unique_values[sub_model_name] = sub_unique_values

        if unique_values:
            unique_values = self._get_deep_unique_from_dict(
                columns=unique_values,
            )
        return unique_values

    def _query(
        self,
    ) -> Select:
        query = select(self.model_class)

        return query

    def _with_related(
        self,
        query: QueryType,
        with_related: Sequence[Any] | None = None,  # type: ignore[override]
    ) -> QueryType:
        if with_related:
            query = query.options(*with_related)
        return query

    def _apply_projection(
        self,
        query: QueryType,
        projection: list[str] | None,
    ) -> QueryType:
        if not projection:
            return query

        for field in projection:
            self._validate_params(field)

        columns = []
        for field in projection:
            if "." in field:
                rel_name, column = field.split(".")
                rel_model = aliased(
                    getattr(self.model_class, rel_name).property.mapper.class_,
                )
                columns.append(getattr(rel_model, column))
            else:
                columns.append(getattr(self.model_class, field))

        return query.options(load_only(*columns))

    def _maybe_join(
        self,
        query: QueryType,
        field: str,
    ) -> QueryType:
        if "." in field:
            relationship_name, column_name = field.split(".")
            model = aliased(
                getattr(
                    self.model_class,
                    relationship_name,
                ).property.mapper.class_,
            )
            return query.join(model)

        return query

    def _get_by[BinaryExpression](
        self,
        field: str,
        value: Any,
        operator: OperatorType = OperatorType.EQUALS,
    ) -> BinaryExpression:  # type: ignore[type-var]
        if operator in [OperatorType.IN, OperatorType.NOT_IN]:
            if type(value) is not list:
                raise BadRequestException(
                    "Для операторов IN, NOT_IN значение value должно быть списком",
                )
        else:
            value = self.__convert_datetime(field, value)

        if "." in field:
            relationship_name, column_name = field.split(".")
            model = aliased(
                getattr(
                    self.model_class,
                    relationship_name,
                ).property.mapper.class_,
            )
        else:
            model = self.model_class
            column_name = field

        match operator:
            case OperatorType.IN:
                return getattr(model, column_name).in_(value)
            case OperatorType.EQUALS:
                return getattr(model, column_name) == value
            case OperatorType.NOT_IN:
                return not_(getattr(model, column_name).in_(value))
            case OperatorType.NOT_EQUAL:
                return getattr(model, column_name) != value
            case OperatorType.GREATER:
                return getattr(model, column_name) > value
            case OperatorType.EQUALS_OR_GREATER:
                return getattr(model, column_name) >= value
            case OperatorType.LESS:
                return getattr(model, column_name) < value
            case OperatorType.EQUALS_OR_LESS:
                return getattr(model, column_name) <= value
            case OperatorType.STARTS_WITH:
                return getattr(model, column_name).startswith(value)
            case OperatorType.ENDS_WITH:
                return getattr(model, column_name).endswith(value)
            case OperatorType.NOT_START_WITH:
                return not_(getattr(model, column_name).startswith(value))
            case OperatorType.NOT_END_WITH:
                return not_(getattr(model, column_name).endswith(value))
            case OperatorType.CONTAINS:
                return getattr(model, column_name).contains(value)
            case OperatorType.NOT_CONTAIN:
                return (not_(getattr(model, column_name).contains(value)),)  # type: ignore[return-value]
            case _:
                raise BadRequestException(
                    f"Оператор {operator} не поддерживается",
                )

    def _filter(
        self,
        query: Select,
        filter_request: FilterRequest,
    ) -> Select:
        params: list[BinaryExpression] = []
        for param in filter_request.filters:
            params.append(
                self._get_by(
                    field=param.field,
                    value=param.value,
                    operator=param.operator,
                ),
            )

        match filter_request.type:
            case FilterType.OR:
                query = query.where(or_(*params))
            case FilterType.AND:
                query = query.where(and_(*params))
            case _:
                raise BadRequestException(
                    f"Тип фильтрации {filter_request.type} не поддерживается",
                )

        return query

    def _paginate(
        self,
        query: Select,
        skip: int = 0,
        limit: int = 100,
    ) -> Select:
        if limit > -1:
            query = query.offset(skip).limit(limit)
        return query

    def _sort_by(
        self,
        query: Select,
        sort_by: str | None = None,
        sort_type: SortType | None = SortType.asc,
    ) -> Select:
        if sort_by is None:
            if hasattr(self.model_class, "updated_at"):
                sort_by = "updated_at"
            else:
                return query
        self._validate_params(sort_by)

        try:
            order_column = getattr(self.model_class, sort_by)
        except AttributeError as exc:
            raise BadRequestException(
                f"Поля {sort_by} нет в полях сущности {self.model_class.__name__}",
            ) from exc

        if sort_type == SortType.desc:
            return query.order_by(order_column.desc())

        return query.order_by(order_column.asc())

    async def _all(self, query: Select) -> list[ModelType]:
        query = await self.session.scalars(query)
        return query.all()

    async def _one_or_none(self, query: Select) -> ModelType | None:
        query = await self.session.scalars(query)
        return query.one_or_none()

    async def _count(self, query: Select) -> int:
        query = query.subquery()
        query = await self.session.scalars(
            select(func.count()).select_from(query),
        )
        return query.one()

    def __convert_datetime(
        self,
        field: str,
        value: Any,
    ) -> datetime | Any:
        if issubclass(
            self._get_model_field_type(self.model_class, field),
            datetime,
        ):
            try:
                return datetime.fromisoformat(value)
            except ValueError as exc:
                raise FieldException(
                    f"Некорректный формат времени для поля {field}. "
                    "Ожидается ISO формат.",
                ) from exc
            except TypeError as exc:
                raise FieldException(
                    f"Некорректный тип для поля {field}: "
                    f"ожидается str, "
                    f"получено {type(value).__name__}",
                ) from exc
        return value

    def _get_model_field_type(
        self,
        _model: ModelType,
        _field: str,
    ) -> type:
        field_type = getattr(_model, _field).type.python_type
        return field_type

    def _has_field(self, field: str) -> bool:
        return field in self.model_class.__mapper__.columns.keys()
