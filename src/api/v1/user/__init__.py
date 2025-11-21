from fastapi import APIRouter

from .user import router as router_user

router = APIRouter()
router.include_router(router=router_user)

__all__ = ("router",)
