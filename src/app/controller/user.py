"""User controller."""

from pydantic import BaseModel

from src.app.model import User
from src.app.repository import (
    UserRepository,
)
from src.core.controller import SQLAlchemyController


class UserController(SQLAlchemyController[User]):
    """User controller."""

    def __init__(
        self,
        user_repository: UserRepository,
        exclude_fields: list[str],
        response_scheme: BaseModel,
    ):
        super().__init__(
            model=User,
            repository=user_repository,
            exclude_fields=exclude_fields,
            response_scheme=response_scheme,
        )
        self.user_repository = user_repository
