from fastapi import APIRouter

from .auth import router as router_auth

router = APIRouter()
router.include_router(router=router_auth)

__all__ = ("router",)
