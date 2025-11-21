"""Base model sqlalchemy."""

from typing import Any

from sqlalchemy import MetaData
from sqlalchemy.orm import DeclarativeBase, declared_attr

from src.core.database.meta import meta


class Base(DeclarativeBase):
    """База для всех моделей sqlalchemy."""

    metadata: MetaData = meta  # type: ignore[misc]
    __abstract__: bool = True

    @declared_attr.directive
    def __tablename__(cls) -> str:
        """Дефолтное значение для __tablename__."""
        return cls.__name__.lower()

    def model_dump(self) -> dict[str, Any]:
        """SQLAlchemy object to dict."""
        result = self.__dict__
        result.pop("_sa_instance_state", None)
        return result
