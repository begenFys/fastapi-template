"""User repository."""

from sqlalchemy import Select
from sqlalchemy.ext.asyncio import AsyncSession

from src.app.model import User
from src.core.repository import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository[User, AsyncSession, Select]):  # type: ignore[type-arg]
    """User repository."""

    pass
