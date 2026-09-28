import logging
from datetime import UTC, datetime, timedelta

import jwt
from pydantic import BaseModel

from app.config.config import settings

logger = logging.getLogger(__name__)


class TokenPayload(BaseModel):
    sub: str
    exp: int
    iat: int


class JWTService:
    def __init__(self, secret_key: str, algorithm: str) -> None:
        self.secret_key = secret_key
        self.algorithm = algorithm

    def encode(self, sub: str, expires_delta: timedelta, now: datetime | None = None) -> str:
        now = now or datetime.now(UTC)
        payload = TokenPayload(
            sub=sub,
            iat=int(now.timestamp()),
            exp=int((now + expires_delta).timestamp()),
        )
        return jwt.encode(payload.model_dump(), self.secret_key, algorithm=self.algorithm)

    def decode(self, token: str) -> TokenPayload:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError as exc:
            logger.debug("JWT decode failed: token expired")
            raise ValueError("Token has expired") from exc
        except jwt.InvalidTokenError as exc:
            logger.warning("JWT decode failed: invalid token")
            raise ValueError("Invalid token") from exc
        return TokenPayload(**payload)


def get_jwt_service() -> JWTService:
    return JWTService(secret_key=settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
