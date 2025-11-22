"""Factory."""

from functools import partial
from typing import TYPE_CHECKING

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session

from src.app.scheme.response.user import UserResponse
from src.core.database.dependency import PostgresSession
from src.core.setting import settings

if TYPE_CHECKING:
    from src.app.controller import (
        UserController,
    )

from src.app.model import (
    User,
)
from src.app.repository import (
    UserRepository,
)
from src.core.database.session import db_session


class Factory:
    """Factory."""

    # Repositories
    user_repository = partial(UserRepository, model=User)

    def get_user_controller(
        self,
        db_session: AsyncSession | async_scoped_session[AsyncSession] = Depends(
            PostgresSession(db_session=db_session),
        ),
    ) -> "UserController":
        """Get user controller."""
        from src.app.controller import UserController

        return UserController(
            user_repository=self.user_repository(db_session=db_session),
            exclude_fields=settings.EXCLUDE_FIELDS,
            response_scheme=UserResponse,  # type: ignore[arg-type]
        )
