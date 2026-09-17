import logging

import uvicorn

from app.config.config import settings
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s %(name)s %(levelname)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

if __name__ == "__main__":
    uvicorn.run(
        "app.app:app",
        host="0.0.0.0",
        port=settings.port,
        log_level="debug" if settings.debug else "info",
        access_log=settings.debug,
        reload=settings.debug,
    )