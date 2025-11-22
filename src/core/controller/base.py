# ruff: noqa: W505
# mypy: disable-error-code="type-arg,valid-type,name-defined,arg-type,attr-defined"
"""Базовый контроллер."""

from abc import ABC, abstractmethod
from collections.abc import Callable, Sequence
from typing import Any
from uuid import UUID

from pydantic import BaseModel

from src.core.exception.base import (
    NotFoundException,
    UnprocessableEntityException,
)
from src.core.helper.scheme.request.filter import (
    FilterParam,
    FilterRequest,
)
from src.core.helper.scheme.response.count import CountResponse
from src.core.helper.scheme.response.for_filter import (
    ForFiltersResponse,
)
from src.core.helper.scheme.response.pagination import (
    PaginationResponse,
)
from src.core.helper.type.controller import DTOMode
from src.core.helper.type.filter import FilterType, OperatorType
from src.core.helper.type.sort import SortType
from src.core.repository import BaseRepository


class BaseController[ModelType](ABC):
    """Базовый класс для контроллера данных."""

    def __init__(
        self,
        model: ModelType,
        repository: BaseRepository,
        exclude_fields: set[str],
        response_scheme: BaseModel,
    ):
        self.model_class = model
        self.repository = repository
        self.exclude_fields = exclude_fields
        self.response_scheme = response_scheme

    @abstractmethod
    async def processing_transaction(
        self,
        function: Callable,
        *args: Any,
        **kwargs: Any,
    ) -> Any:
        """Метод для обработки транзакции."""
        raise NotImplementedError

    def dto(
        self,
        value: ModelType | list[ModelType],
        dto_mode: DTOMode,
    ) -> BaseModel | dict[str, Any] | list[BaseModel | dict[str, Any]]:
        """Mapping ModelType in dict or BaseModel."""
        match dto_mode:
            case DTOMode.pydantic:
                if isinstance(value, list):
                    return [
                        self.response_scheme.model_validate(el) for el in value
                    ]
                return self.response_scheme.model_validate(value)
            case DTOMode.dict:
                if isinstance(value, list):
                    return [el.model_dump() for el in value]  # type: ignore[union-attr]
                return value.model_dump()

    def transactional(function):  # type: ignore
        """Декоратор для транзакций."""

        async def wrapper(self, *args, **kwargs):  # type: ignore
            """Функция-обертка."""
            response = await self.processing_transaction(
                function,
                *args,
                **kwargs,
            )
            return response

        return wrapper

    async def get_by(
        self,
        field: str,
        value: Any,
        operator: OperatorType = OperatorType.EQUALS,
        skip: int = 0,
        limit: int = 100,
        sort_by: str | None = None,
        sort_type: SortType | None = SortType.asc,
        unique: bool = False,
        projection: list[str] | None = None,
        with_related: Sequence[Any] | bool | None = None,
        dto_mode: DTOMode | None = None,
    ) -> (
        ModelType
        | PaginationResponse
        | BaseModel
        | dict[str, Any]
        | list[BaseModel | dict[str, Any]]
    ):
        """Возвращает экземпляр модели, соответствующий значению.

        Args:
            field: Поле для получения.
            value: Значение для совпадения.
            operator: Оператор сравнения.
            skip: Количество записей для пропуска.
            limit: Количество записей для возврата.
            sort_by: Поле для сортировки.
            sort_type: Направление сортировки.
            unique: Уникальность значения.
            projection: Выборка по определённым полям.
            with_related: Указание подтягивание отношений с другими моделями.
            dto_mode: Маппинг ModelType в BaseModel или dict

        Returns:
            Экземпляры модели.
        """
        result = await self.repository.get_by(
            field=field,
            value=value,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_type=sort_type,
            operator=operator,
            unique=unique,
            projection=projection,
            with_related=with_related,
        )
        if not result:
            raise NotFoundException(
                f"{self.model_class.__name__} {field} со значением {value} не существует",  # noqa: E501
            )

        if unique:
            if dto_mode:
                return self.dto(value=result, dto_mode=dto_mode)
            return result

        return await self.make_pagination_response(
            data=self.dto(value=result, dto_mode=dto_mode)
            if dto_mode
            else result,
            skip=skip,
            limit=limit,
            filter_request=FilterRequest(
                filters=[
                    FilterParam(field=field, value=value, operator=operator),
                ],
                type=FilterType.AND,
            ),
        )

    async def get_by_filters(
        self,
        filter_request: FilterRequest | None = None,
        skip: int = 0,
        limit: int = 100,
        sort_by: str | None = None,
        sort_type: SortType | None = SortType.asc,
        unique: bool = False,
        projection: list[str] | None = None,
        with_related: Sequence[Any] | bool | None = None,
        dto_mode: DTOMode | None = None,
    ) -> (
        ModelType
        | list[ModelType]
        | PaginationResponse
        | BaseModel
        | dict[str, Any]
        | list[BaseModel | dict[str, Any]]
    ):
        """Получает экземпляр модели, соответствующий фильтрам.

        Args:
            filter_request: Фильтры для совпадения.
            skip: Количество записей для пропуска.
            limit: Количество записей для возврата.
            sort_by: Поле для сортировки.
            sort_type: Направление сортировки.
            unique: Уникальность значения.
            projection: Выборка по определённым полям.
            with_related: Указание подтягивание отношений с другими моделями.
            dto_mode: Маппинг ModelType в BaseModel или dict

        Returns:
            Экземпляры модели или уникальный экземпляр.
        """
        result = await self.repository.get_by_filters(
            filter_request=filter_request,
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_type=sort_type,
            unique=unique,
            projection=projection,
            with_related=with_related,
        )

        if unique:
            if result:
                if dto_mode:
                    return self.dto(value=result, dto_mode=dto_mode)
                return result
            else:
                raise NotFoundException(
                    f"Уникального {self.model_class.__name__} с данными фильтрами не существует",
                )

        return await self.make_pagination_response(
            data=self.dto(value=result, dto_mode=dto_mode)
            if dto_mode
            else result,
            skip=skip,
            limit=limit,
            filter_request=filter_request,
        )

    async def count(
        self,
        filter_request: FilterRequest | None = None,
    ) -> CountResponse:
        """Возвращает количество записей в модели по фильтрам.

        Args:
            filter_request: Фильтры для совпадения.

        Returns:
            Количество записей.
        """
        return CountResponse(
            count=await self.repository.count(filter_request=filter_request),
        )

    async def get_for_filters(
        self,
        filter_request: FilterRequest | None = None,
        sort_type: SortType | None = SortType.asc,
    ) -> ForFiltersResponse:
        """Возвращает словарь полей с их уникальными значениями."""
        for_filters = await self.repository.get_columns_unique_values(
            filter_request=filter_request,
            sort_type=sort_type,
        )
        return ForFiltersResponse(columns=for_filters)

    async def get_by_id(
        self,
        id_: int,
        projection: list[str] | None = None,
        with_related: Sequence[Any] | bool | None = None,
        dto_mode: DTOMode | None = None,
    ) -> ModelType | BaseModel | dict[str, Any]:
        """Возвращает экземпляр модели, соответствующий идентификатору.

        Args:
            id_: Идентификатор для совпадения.
            projection: Выборка по определённым полям.
            with_related: Указание подтягивание отношений с другими моделями.
            dto_mode: Маппинг ModelType в BaseModel или dict

        Returns:
            Экземпляр модели.
        """
        result = await self.repository.get_by(
            field="id",
            value=id_,
            unique=True,
            projection=projection,
            with_related=with_related,
        )
        if not result:
            raise NotFoundException(
                f"{self.model_class.__name__} c id: {id_} не существует",
            )

        if dto_mode:
            return self.dto(value=result, dto_mode=dto_mode)  # type: ignore[return-value]

        return result  # type: ignore[return-value]

    async def get_by_uuid(
        self,
        uuid: UUID,
        with_related: Sequence[Any] | bool | None = None,
        dto_mode: DTOMode | None = None,
    ) -> ModelType | BaseModel | dict[str, Any]:
        """Возвращает экземпляр модели, соответствующий UUID.

        Args:
            uuid: UUID для совпадения.
            with_related: Указание подтягивание отношений с другими моделями.
            dto_mode: Маппинг ModelType в BaseModel или dict

        Returns:
            Экземпляр модели.
        """
        result = await self.repository.get_by(
            field="uuid",
            value=uuid,
            unique=True,
            with_related=with_related,
        )
        if not result:
            raise NotFoundException(
                f"{self.model_class.__name__} с uuid: {uuid} не существует",
            )

        if dto_mode:
            return self.dto(value=result, dto_mode=dto_mode)  # type: ignore[return-value]

        return result  # type: ignore[return-value]

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        sort_by: str | None = None,
        sort_type: SortType | None = SortType.asc,
        projection: list[str] | None = None,
        with_related: Sequence[Any] | bool | None = None,
        dto_mode: DTOMode | None = None,
    ) -> PaginationResponse | list[BaseModel | dict[str, Any]]:
        """Возвращает список записей на основе параметров пагинации.

        Args:
            skip: Количество записей для пропуска.
            limit: Количество записей для возврата.
            sort_by: Поле для сортировки.
            sort_type: Направление сортировки.
            projection: Выборка по определённым полям.
            with_related: Указание подтягивание отношений с другими моделями.
            dto_mode: Маппинг ModelType в BaseModel или dict

        Returns:
            Список записей.
        """
        result = await self.repository.get_all(
            skip=skip,
            limit=limit,
            sort_by=sort_by,
            sort_type=sort_type,
            projection=projection,
            with_related=with_related,
        )

        return await self.make_pagination_response(
            data=self.dto(value=result, dto_mode=dto_mode)
            if dto_mode
            else result,
            skip=skip,
            limit=limit,
        )

    @transactional
    async def create(self, attributes: dict[str, Any]) -> ModelType:
        """Создает новый объект в базе данных.

        Args:
            attributes: Атрибуты для создания объекта.

        Returns:
            Созданный объект.
        """
        created_model = await self.repository.create(attributes=attributes)
        return created_model

    @transactional
    async def delete(self, model: ModelType) -> ModelType:
        """Удаляет объект из базы данных.

        Args:
            model: Модель для удаления.

        Returns:
            Удаленный объект.
        """
        deleted_model = await self.repository.delete(model=model)
        return deleted_model

    @transactional
    async def update(
        self,
        model: ModelType,
        attributes: dict[str, Any],
    ) -> ModelType:
        """Обновляет объект в базе данных.

        Args:
            model: Модель для обновления.
            attributes: Атрибуты для обновления объекта.

        Returns:
            Обновленный объект.
        """
        for field in attributes:
            if field in self.exclude_fields:
                raise UnprocessableEntityException(
                    f"Поле {field} запрещёно для обновления",
                )
        updated_model = await self.repository.update(
            model=model,
            attributes=attributes,
        )
        return updated_model

    @transactional
    async def update_by_filters(
        self,
        filter_request: FilterRequest,
        attributes: dict[str, Any],
    ) -> list[ModelType]:
        """Обновляет объекты по фильтрам.

        Args:
           filter_request: Фильтры для поиска.
           attributes: Атрибуты для обновления экземпляров модели.

        Returns:
            Обновлённые объекты.
        """
        for field in attributes:
            if field in self.exclude_fields:
                raise UnprocessableEntityException(
                    f"Поле {field} запрещёно для обновления",
                )
        updated_models = await self.repository.update_by_filters(
            filter_request=filter_request,
            attributes=attributes,
        )
        return updated_models

    @transactional
    async def delete_by_filters(
        self,
        filter_request: FilterRequest,
    ) -> list[ModelType]:
        """Удаляет объекты базы данных по фильтрам.

        Args:
           filter_request: Фильтры для поиска.

        Returns:
            Удалённые объекты.
        """
        deleted_models = await self.repository.delete_by_filters(
            filter_request=filter_request,
        )
        return deleted_models

    async def make_pagination_response(
        self,
        data: Sequence[ModelType],
        skip: int = 0,
        limit: int = 100,
        filter_request: FilterRequest | None = None,
    ) -> PaginationResponse:
        """Возвращает ответ для пагинации с численными полями.

        Args:
            data: Сущность или список сущностей ответа.
            skip: Кол-во записей для пропуска.
            limit: Кол-во записей для возврата.
            filter_request: Фильтры для совпадения.
        """
        total_count = (await self.count(filter_request=filter_request)).count
        page = skip // limit + 1 if limit > 0 else 1
        page_size = len(data)
        total_pages = (total_count + limit - 1) // limit if limit > 0 else 1

        return PaginationResponse(
            data=data,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
            total_count=total_count,
        )

    def __repr__(self) -> str:
        """Возвращает строковое представление объекта.

        Returns:
            Строковое представление объекта.
        """
        return f"<{self.__class__.__name__}>"
