"""User model."""

import uuid

from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql.sqltypes import UUID, String, Text

from src.core.database.base import Base
from src.core.database.mixin import AsDictMixin, TimestampMixin


class User(Base, TimestampMixin, AsDictMixin):
    """User model."""

    __tablename__ = "user"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    username: Mapped[str] = mapped_column(
        String(length=255),
        unique=True,
        nullable=False,
    )
    email: Mapped[str] = mapped_column(
        String(length=255),
        unique=True,
        nullable=False,
        index=True,
    )
    hashed_password: Mapped[str] = mapped_column(
        Text,
        nullable=False,
    )
