import logging

from fastapi import APIRouter

logger = logging.getLogger(__name__)

router = APIRouter(tags=["health"])


@router.get("/health")
async def health_check():
    logger.debug("Health check endpoint called")
    return {"status": "healthy"}


__all__ = ["router"]
