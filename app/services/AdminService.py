from fastapi import Depends
from app.database.models import User, UserRole
from app.exceptions import ApiException

from app.config.config import Settings, settings
from app.services.AuthService import AuthService, get_auth_service
from app.database.actions import create_user, get_user_by_email, set_user_role



class AdminService:
    def __init__(self, 
        config: Settings,
        auth_service: AuthService
    ):
        self._auth_service = auth_service
        self._config = config

    async def _verify_admin(self, user: User) -> None:
        if user.role != UserRole.ADMIN:
            raise ApiException(403, "forbidden", "User is not an admin")
        

    async def set_user_role(self, email: str, role: str) -> User:
        user = await self._auth_service._require_user(email)
        updated_user = await set_user_role(user, role)
        return updated_user


def get_admin_service(
    config: Settings = settings,
    auth_service: AuthService = Depends(get_auth_service),
) -> AdminService:
    return AdminService(config=config, auth_service=auth_service)