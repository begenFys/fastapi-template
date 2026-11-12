"""Auth router."""

from http import HTTPStatus
from typing import Annotated

from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from src.app.controller import AuthController
from src.app.factory import Factory
from src.app.scheme.request.auth import RefreshRequest, RegisterRequest
from src.app.scheme.response.token import TokenResponse
from src.app.scheme.response.user import UserResponse

router = APIRouter()

Controller = Annotated[AuthController, Depends(Factory().get_auth_controller)]


@router.post(
    path="/register",
    status_code=HTTPStatus.CREATED,
    response_model=UserResponse,
)
async def register(data: RegisterRequest, controller: Controller) -> object:
    """Create a user."""
    return await controller.register(data)


@router.post(path="/login", response_model=TokenResponse)
async def login(
    form: Annotated[OAuth2PasswordRequestForm, Depends()],
    controller: Controller,
) -> TokenResponse:
    """Log in with username or email and get a token pair.

    Takes an OAuth2 password form, so the Authorize button in Swagger UI
    works out of the box.
    """
    return await controller.login(login=form.username, password=form.password)


@router.post(path="/refresh", response_model=TokenResponse)
async def refresh(
    data: RefreshRequest,
    controller: Controller,
) -> TokenResponse:
    """Exchange a refresh token for a new pair. The old one stops working."""
    return await controller.refresh(data.refresh_token)


@router.post(path="/logout", status_code=HTTPStatus.NO_CONTENT)
async def logout(data: RefreshRequest, controller: Controller) -> None:
    """Revoke a refresh token."""
    await controller.logout(data.refresh_token)
