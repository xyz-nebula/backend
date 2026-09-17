from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.exceptions import ApiException
from app.services.JWTService import JWTService, TokenPayload, get_jwt_service

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_token_payload(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    jwt_service: JWTService = Depends(get_jwt_service),
) -> TokenPayload:
    if credentials is None:
        raise ApiException(401, "missing_token", "Missing bearer token")
    try:
        return jwt_service.decode(credentials.credentials)
    except ValueError as exc:
        code = "token_expired" if "expired" in str(exc) else "invalid_token"
        raise ApiException(401, code, str(exc)) from exc
