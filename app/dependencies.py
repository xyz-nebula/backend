import logging

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.database.actions import get_user_by_uuid
from app.database.models import User, UserRole
from app.exceptions import ApiException
from app.services.JWTService import JWTService, TokenPayload, get_jwt_service

logger = logging.getLogger(__name__)

bearer_scheme = HTTPBearer(auto_error=False)


def get_current_token_payload(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    jwt_service: JWTService = Depends(get_jwt_service),
) -> TokenPayload:
    if credentials is None:
        logger.debug("Request rejected: missing bearer token")
        raise ApiException(401, "missing_token", "Missing bearer token")
    try:
        return jwt_service.decode(credentials.credentials)
    except ValueError as exc:
        code = "token_expired" if "expired" in str(exc) else "invalid_token"
        logger.warning("Request rejected: %s", code)
        raise ApiException(401, code, str(exc)) from exc


async def get_current_admin(
    payload: TokenPayload = Depends(get_current_token_payload),
) -> User:
    user = await get_user_by_uuid(payload.sub)
    if user is None:
        raise ApiException(401, "invalid_token", "User no longer exists")
    if user.role != UserRole.ADMIN:
        raise ApiException(403, "forbidden", "User is not an admin")
    return user
