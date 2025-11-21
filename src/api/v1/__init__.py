"""API роутер V1."""

from fastapi.routing import APIRouter

from src.api.v1 import user

router = APIRouter()

router.include_router(
    router=user.router,
    prefix="/user",
    tags=["User"],
)

__all__ = ("router",)
