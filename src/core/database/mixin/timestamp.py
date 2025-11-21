"""Timestamp mixin."""

from sqlalchemy import DateTime, func
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Mapped, mapped_column


class TimestampMixin:
    """Timestamp mixin."""

    @declared_attr
    def created_at(cls) -> Mapped[DateTime]:
        """Column created_at."""
        return mapped_column(
            DateTime,
            default=func.now(),
            nullable=False,
        )

    @declared_attr
    def updated_at(cls) -> Mapped[DateTime]:
        """Column updated_at."""
        return mapped_column(
            DateTime,
            default=func.now(),
            onupdate=func.now(),
            nullable=False,
        )
