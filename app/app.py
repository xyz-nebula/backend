import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise

from app.api.v1 import router as v1_router
from app.api.v1.routers import health_router
from app.middleware.middleware import JWTAuthenticationMiddleware\

from app.config.config import settings

logging.basicConfig(
    level=logging.DEBUG if settings.debug else logging.INFO,
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Website Profile Backend",
    description="A backend service for managing website profiles and user authentication.",
    version="1.0.0",
)

register_tortoise(
    app,
    db_url=settings.db_url,
    modules={"models": ["nl_models.models"]},
    generate_schemas=True,
    add_exception_handlers=True,
)

app.include_router(v1_router)
app.include_router(health_router)

__all__ = ["app"]