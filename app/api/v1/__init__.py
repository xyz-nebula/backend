from fastapi import APIRouter

from .routers import auth_router

router = APIRouter(prefix="/v1")

router.include_router(auth_router)
