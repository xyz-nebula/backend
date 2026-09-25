from fastapi import Depends

from app.config.config import Settings, settings
from app.database.actions import set_user_role
from app.database.models import User, UserRole
from app.exceptions import ApiException
from app.services.AuthService import AuthService, get_auth_service


class AdminService:
    def __init__(self, config: Settings, auth_service: AuthService):
        self._auth_service = auth_service
        self._config = config

    async def _verify_admin(self, user: User) -> None:
        if user.role != UserRole.ADMIN:
            raise ApiException(403, "forbidden", "User is not an admin")

    async def set_user_admin(self, user: User, code: str) -> User:
        if code != self._config.admin_code:
            raise ApiException(400, "invalid_code", "Invalid admin code")
        return await self.set_user_role(user, UserRole.ADMIN)

    async def set_user_role(self, user: User, role: UserRole) -> User:
        updated_user = await set_user_role(user, role)
        return updated_user


def get_admin_service(
    auth_service: AuthService = Depends(get_auth_service),
) -> AdminService:
    return AdminService(config=settings, auth_service=auth_service)
