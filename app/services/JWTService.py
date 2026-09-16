import jwt
from pydantic import BaseModel

from app.config.config import settings


class TokenPayload(BaseModel):
    sub: str
    exp: int
    iat: int


class JWTService:
    def __init__(self, secret_key: str, algorithm: str) -> None:
        self.secret_key = secret_key
        self.algorithm = algorithm

    def decode(self, token: str) -> TokenPayload:
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
        except jwt.ExpiredSignatureError as exc:
            raise ValueError("Token has expired") from exc
        except jwt.InvalidTokenError as exc:
            raise ValueError("Invalid token") from exc
        return TokenPayload(**payload)


def get_jwt_service() -> JWTService:
    return JWTService(secret_key=settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
