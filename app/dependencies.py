from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.services.JWTService import JWTService, TokenPayload, get_jwt_service

bearer_scheme = HTTPBearer()


def get_current_token_payload(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    jwt_service: JWTService = Depends(get_jwt_service),
) -> TokenPayload:
    try:
        return jwt_service.decode(credentials.credentials)
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc
