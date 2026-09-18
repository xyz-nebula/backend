from fastapi import APIRouter

from .routers import auth_router, chat_router

router = APIRouter(prefix="/v1")

router.include_router(auth_router)
router.include_router(chat_router)
