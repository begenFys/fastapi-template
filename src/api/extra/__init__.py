"""Extra API роутер."""

from fastapi.routing import APIRouter

from src.api.extra import monitoring

router = APIRouter()

router.include_router(
    router=monitoring.router,
    tags=["Monitoring"],
)

__all__ = ["router"]
