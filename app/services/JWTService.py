import datetime

import jwt
from pydantic import BaseModel

from app.config.config import settings
from app.domain.exceptions.JWTExceptions import *


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
            raise JWTExpiredError("Token has expired") from exc
        except jwt.InvalidTokenError as exc:
            raise JWTInvalidTokenError("Invalid token") from exc
        return TokenPayload(**payload)
    
    def create_access_token(self, refresh_token: str) -> str:
        """Create a new access token using a refresh token."""
        refresh_payload = self.decode(refresh_token)  # Validate the refresh token
        
        expire = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=settings.jwt_access_token_expire_minutes)
        payload = {
            "sub": refresh_payload.sub,
            "exp": expire,
            "iat": datetime.datetime.now(datetime.timezone.utc),
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def create_refresh_token(self, user_id: str) -> str:
        """Create a new refresh token."""
        ...
        
    
def get_jwt_service() -> JWTService:
    return JWTService(secret_key=settings.jwt_secret_key, algorithm=settings.jwt_algorithm)
