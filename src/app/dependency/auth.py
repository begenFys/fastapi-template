"""Current user dependency."""

from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from src.app.controller import AuthController
from src.app.factory import Factory
from src.app.model import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    controller: Annotated[
        AuthController,
        Depends(Factory().get_auth_controller),
    ],
) -> User:
    """Return the user from the `Authorization: Bearer` access token."""
    return await controller.get_current_user(token)


CurrentUser = Annotated[User, Depends(get_current_user)]
