"""User router."""

from fastapi import APIRouter

from src.app.dependency import CurrentUser
from src.app.scheme.response.user import UserResponse

router = APIRouter()


@router.get(path="/me", response_model=UserResponse)
async def get_me(user: CurrentUser) -> object:
    """Return the current user."""
    return user
