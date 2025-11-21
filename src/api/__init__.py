"""Main API router."""

from fastapi.routing import APIRouter

from src.api import extra, v1

main_router = APIRouter(prefix="/api")

main_router.include_router(
    router=extra.router,
)

main_router.include_router(
    router=v1.router,
    prefix="/v1",
)

__all__ = ["main_router"]
