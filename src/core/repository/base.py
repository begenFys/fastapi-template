"""Базовый репозиторий."""

# TODO: eng lang and maybe with_related in update and update_by_filters
from abc import ABC, abstractmethod
from collections import defaultdict
from collections.abc import Sequence
from typing import (
    Any,
)

from src.core.exception.base import NotFoundException
from src.core.exception.database import FieldException
from src.core.helper.scheme.request.filter import (
    FilterParam,
    FilterRequest,
)
from src.core.helper.type.filter import FilterType, OperatorType
from src.core.helper.type.sort import SortType


class BaseRepository[ModelType, SessionType, QueryType](ABC):
    """Базовый класс для репозиториев данных."""

    def __init__(self, model: ModelType, db_session: SessionType):
        self.session = db_session
        self.model_class = model

    async def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        sort_by: str | None = None,
        sort_type: SortType | None = SortType.asc,
        projection: list[str] | None = None,
        with_related: Sequence[Any] | bool | None = None,
    ) -> list[ModelType]:
        """Возвращает список экземпляров модели.

        Args:
            skip: Количество записей для пропуска.
            limit: Количество записей для возврата.
            sort_by: Поле для сортировки.
            sort_type: Направление сортировки.
            projection: Выборка по определённым полям.
            with_related: Указание подтягивание отношений с другими моделями.

        Returns:
            Список экземпляров модели.
        """
        query = self._query()
        query = self._with_related(query=query, with_related=with_related)
        query = self._apply_projection(query=query, projection=projection)
        query = self._sort_by(query=query, sort_by=sort_by, sort_type=sort_type)
        query = self._paginate(query=query, skip=skip, limit=limit)

        return await self._all(query)

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
    ) -> ModelType | None | list[ModelType]:
        """Возвращает экземпляр модели, соответствующий полю и значению.

        Args:
            field: Поле для совпадения.
            value: Значение для совпадения.
            operator: Оператор сравнения.
            skip: Количество записей для пропуска.
            limit: Количество записей для возврата.
            sort_by: Поле для сортировки.
            sort_type: Направление сортировки.
            unique: Уникальный параметр.
            projection: Выборка по определённым полям.
            with_related: Указание подтягивание отношений с другими моделями.

        Returns:
            Экземпляр модели.
        """
        self._validate_params(field)
        query = self._query()
        query = self._with_related(query=query, with_related=with_related)
        query = self._apply_projection(query=query, projection=projection)
        query = self._filter(
            query=query,
            filter_request=FilterRequest(
                filters=[
                    FilterParam(field=field, value=value, operator=operator),
                ],
                type=FilterType.OR,
            ),
        )

        if unique:
            return await self._one_or_none(query)

        query = self._sort_by(query=query, sort_by=sort_by, sort_type=sort_type)
        query = self._paginate(query=query, skip=skip, limit=limit)

        return await self._all(query)

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
    ) -> ModelType | None | list[ModelType]:
        """Возвращает экземпляры модели, соответствующие фильтрам.

        Args:
            filter_request: Фильтры для совпадения.
            skip: Количество записей для пропуска.
            limit: Количество записей для возврата.
            sort_by: Поле для сортировки.
            sort_type: Направление сортировки.
            unique: Уникальная запись.
            projection: Выборка по определённым полям.
            with_related: Указание подтягивание отношений с другими моделями.

        Returns:
            Список экземпляров модели.
        """
        query = self._query()
        query = self._with_related(query=query, with_related=with_related)
        query = self._apply_projection(query=query, projection=projection)
        if filter_request is not None and len(filter_request.filters) > 0:
            for param in filter_request.filters:
                self._validate_params(param.field)

            query = self._filter(query=query, filter_request=filter_request)

        data: ModelType | None | list[ModelType]

        if unique:
            data = await self._one_or_none(query)
        else:
            query = self._sort_by(
                query=query,
                sort_by=sort_by,
                sort_type=sort_type,
            )
            query = self._paginate(query=query, skip=skip, limit=limit)

            data = await self._all(query)

        return data

    async def count(
        self,
        filter_request: FilterRequest | None = None,
    ) -> int:
        """Возвращает кол-во записей, соответствующих фильтрам.

        Args:
            filter_request: Фильтры для совпадения.

        Returns:
            Кол-во записей.
        """
        query = self._query()
        if filter_request is not None and len(filter_request.filters) > 0:
            for param in filter_request.filters:
                self._validate_params(param.field)
                # query = self._maybe_join(query=query, field=param.field)
            query = self._filter(query, filter_request)
        return await self._count(query)

    async def create(self, attributes: dict[str, Any]) -> ModelType:
        """Создает экземпляр модели.

        Args:
            attributes: Атрибуты для создания модели.

        Returns:
            Созданный экземпляр модели.
        """
        for field in attributes:
            self._validate_params(field)
        created_model = self.model_class(**attributes)  # type: ignore[operator]
        await self._create(created_model)
        return created_model

    async def update(
        self,
        model: ModelType,
        attributes: dict[str, Any],
    ) -> ModelType:
        """Обновляет экземпляр модели с заданными атрибутами.

        Args:
            model: Модель для обновления.
            attributes: Атрибуты для обновления экземпляра модели.

        Returns:
            Обновленный экземпляр модели.
        """
        if model is None:
            raise NotFoundException("Сущность не найдена")

        for field, value in attributes.items():
            self._validate_params(field)
            current = getattr(model, field, None)
            if isinstance(current, dict) and isinstance(value, dict):
                self.deep_merge_dict(current, value)
                setattr(model, field, current)
            else:
                setattr(model, field, value)

        await self._update(model)
        return model

    async def delete(self, model: ModelType) -> ModelType:
        """Удаляет экземпляр модели.

        Args:
            model: Модель для удаления.

        Returns:
            Удаленный экземпляр модели.
        """
        if model is None:
            raise NotFoundException("Сущность не найдена")
        await self._delete(model)
        return model

    @abstractmethod
    async def update_by_filters(
        self,
        filter_request: FilterRequest,
        attributes: dict[str, Any],
    ) -> list[ModelType]:
        """Обновляет экземпляры модели по фильтрам.

        Args:
           filter_request: Фильтры для поиска.
           attributes: Атрибуты для обновления экземпляров модели.

        Returns:
            Обновлённые экземпляры модели.
        """
        raise NotImplementedError

    @abstractmethod
    async def delete_by_filters(
        self,
        filter_request: FilterRequest,
    ) -> list[ModelType]:
        """Удаляет экземпляры модели по фильтрам.

        Args:
           filter_request: Фильтры для поиска.

        Returns:
            Удалённые экземпляры модели.
        """
        raise NotImplementedError

    @abstractmethod
    async def get_columns_unique_values(
        self,
        filter_request: FilterRequest | None = None,
        sort_type: SortType | None = SortType.asc,
    ) -> dict[str, list[Any]]:
        """Возвращает словарь уникальных значений полей модели.

        Args:
            filter_request: Запрос для фильтров,
            sort_type: Направление сортировки.

        Notes:
            Фильтрует по get_by_filters и достает уникальные значения.

        Returns:
            Словарь уникальных значений.
        """
        raise NotImplementedError

    def deep_merge_dict(
        self,
        to: dict[str, Any],
        update: dict[str, Any],
    ) -> None:
        """Рекурсивно обновляет значения dict `to` значениями из dict `update`."""
        for k, v in update.items():
            if k in to and isinstance(to[k], dict) and isinstance(v, dict):
                self.deep_merge_dict(to[k], v)
            else:
                to[k] = v

    @abstractmethod
    async def _create(self, model: ModelType) -> None:
        """Вызов метода создания."""
        raise NotImplementedError

    @abstractmethod
    async def _update(self, model: ModelType) -> None:
        """Вызов метода обновления."""
        raise NotImplementedError

    @abstractmethod
    async def _delete(self, model: ModelType) -> None:
        """Вызов метода удаления."""
        raise NotImplementedError

    @abstractmethod
    def _query(
        self,
    ) -> QueryType:
        """Возвращает вызываемый объект, который можно использовать для запроса модели.

        Returns:
            Вызываемый объект, который можно использовать для запроса модели.
        """
        raise NotImplementedError

    @abstractmethod
    def _with_related(
        self,
        query: QueryType,
        with_related: Sequence[Any] | bool | None = None,
    ) -> QueryType:
        """Make query with related.

        Returns:
            QueryType instance.
        """
        raise NotImplementedError

    @abstractmethod
    def _apply_projection(
        self,
        query: QueryType,
        projection: list[str] | None,
    ) -> QueryType:
        """Применяет проекцию(выборку определённых полей) к запросу."""
        raise NotImplementedError

    @abstractmethod
    def _maybe_join(
        self,
        query: QueryType,
        field: str,
    ) -> QueryType:
        """Возвращает запрос, который может указать на использование связанной сущности.

        Returns:
            Запрос со связанной сущностью.
        """
        raise NotImplementedError

    @abstractmethod
    async def _all(self, query: QueryType) -> list[ModelType]:
        """Возвращает все результаты запроса.

        Args:
            query: Запрос для выполнения.

        Returns:
            Список экземпляров модели.
        """
        raise NotImplementedError

    @abstractmethod
    async def _one_or_none(self, query: QueryType) -> ModelType | None:
        """Возвращает первый результат запроса или None.

        Args:
            query: Запрос для выполнения.

        Returns:
            Экземпляр модели.
        """
        raise NotImplementedError

    @abstractmethod
    def _get_by[ExpressionType](
        self,
        field: str,
        value: Any,
        operator: OperatorType = OperatorType.EQUALS,
    ) -> ExpressionType:  # type: ignore[type-var]
        """Возвращает запрос по указанному полю.

        Args:
            field: Колонка для фильтрации.
            value: Значение для фильтрации.
            operator: Оператор сравнения.

        Notes:
            В этом месте происходит валидация поля и значения.

        Returns:
            Выражение для нужного оператора.
        """
        raise NotImplementedError

    @abstractmethod
    def _filter(
        self,
        query: QueryType,
        filter_request: FilterRequest,
    ) -> QueryType:
        """Добавляет фильтры для query.

        Args:
            query: Запрос.
            filter_request: Запрос для фильтров.

        Notes:
            Использует _get_by для получения значения поля.

        Returns:
            Запрос(QueryType)
        """
        raise NotImplementedError

    @abstractmethod
    async def _count(self, query: QueryType) -> int:
        """Возвращает количество записей.

        Args:
            query: Запрос для выполнения.

        Returns:
            Количество экземпляров модели.
        """
        raise NotImplementedError

    @abstractmethod
    def _paginate(
        self,
        query: QueryType,
        skip: int = 0,
        limit: int = -1,
    ) -> QueryType:
        """Возвращает запрос, в котором применена пагинация.

        Args:
            query: Запрос для сортировки.
            skip: Количество записей для пропуска.
            limit: Количество записей для возврата.

        Returns:
            Отпагиннированный запрос.
        """
        raise NotImplementedError

    @abstractmethod
    def _sort_by(
        self,
        query: QueryType,
        sort_by: str | None,
        sort_type: SortType | None = SortType.asc,
    ) -> QueryType:
        """Возвращает запрос, отсортированный по указанной колонке.

        Args:
            query: Запрос для сортировки.
            sort_by: Поле для сортировки.
            sort_type: Направление сортировки.

        Returns:
            Отсортированный запрос.
        """
        raise NotImplementedError

    def _get_deep_unique_from_dict(
        self,
        columns: dict[str, Any],
    ) -> dict[str, Any] | list[dict[str, Any]]:
        """Рекурсивно обходит словарь/список/примитив.

        1) Если встретили словарь - углубляемся по ключам.
        2) Если встретили список из словарей - собираем уникальные значения по
            ключам, рекурсивно обрабатывая значения.
        3) Если встретили список "простых" (или смешанных) элементов - рекурсивно
            обрабатываем каждый элемент и сохраняем только уникальные.
        4) Если встретили примитив (int, str, bool и т.д.) - возвращаем как есть.
        """
        # Если это словарь, обрабатываем по ключам
        if isinstance(columns, dict):
            result = {}
            for key, value in columns.items():
                result[key] = self._get_deep_unique_from_dict(value)
            return result

        # Если это список
        elif isinstance(columns, list):
            # Проверяем, что все элементы - словари
            if all(isinstance(item, dict) for item in columns):
                # Собираем уникальные значения по ключам
                aggregated = defaultdict(list)
                for item in columns:
                    for k, v in item.items():
                        processed_v = self._get_deep_unique_from_dict(v)
                        if processed_v not in aggregated[k]:
                            aggregated[k].append(processed_v)
                return self._get_deep_unique_from_dict(aggregated)

            else:
                # Список не из одних dict (или смешанный) — рекурсивно обрабатываем каждый элемент
                processed_list = []
                for item in columns:
                    processed_item = self._get_deep_unique_from_dict(item)
                    if processed_item not in processed_list:
                        processed_list.append(processed_item)
                return processed_list

        # Если это не список и не словарь (примитив: int, str, bool, и т.п.)
        else:
            return columns

    @abstractmethod
    def _get_model_field_type(
        self,
        _model: ModelType,
        _field: str,
    ) -> type:
        """Получить python-style тип поля."""
        raise NotImplementedError

    def _resolve_field_relation(
        self,
        field: str,
    ) -> tuple[ModelType, str]:
        """Получение модели и имени колонки из поля."""
        raise NotImplementedError

    @abstractmethod
    def _has_field(self, field: str) -> bool:
        """Проверяет, есть ли поле в модели (или корневое поле, если вложенное)."""
        pass

    def _validate_params(
        self,
        field: str,
    ) -> None:
        """Валидация параметров по наличию поля в модели."""
        root_field = field.split(".")[0]
        if not self._has_field(root_field):
            raise FieldException(
                message=f"Поле '{root_field}' не найдено в {self.model_class.__name__}",  # type: ignore[attr-defined]
            )
