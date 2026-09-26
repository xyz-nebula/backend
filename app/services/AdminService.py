from uuid import UUID

from fastapi import Depends

from app.config.config import Settings, settings
from app.database.actions import delete_case, set_user_role
from app.database.models import Case, CaseDifficulty, User, UserRole
from app.exceptions import ApiException
from app.services.AuthService import AuthService, get_auth_service
from app.services.CaseService import CaseService, get_case_service


class AdminService:
    def __init__(self, config: Settings, auth_service: AuthService, case_service: CaseService):
        self._auth_service = auth_service
        self._case_service = case_service
        self._config = config

    async def _verify_admin(self, user: User) -> None:
        if user.role != UserRole.ADMIN:
            raise ApiException(403, "forbidden", "User is not an admin")

    async def create_case(
        self,
        name: str,
        description: str,
        category: str,
        difficulty: CaseDifficulty,
        time_limit: int,
        system_prompt: str,
        goal: str,
        synopsis: str,
        first_role: str,
        second_role: str,
        first_role_preparations: str,
        second_role_preparations: str,
    ) -> Case:
        return await self._case_service.create_case(
            name=name,
            description=description,
            category=category,
            difficulty=difficulty,
            time_limit=time_limit,
            system_prompt=system_prompt,
            goal=goal,
            synopsis=synopsis,
            first_role=first_role,
            second_role=second_role,
            first_role_preparations=first_role_preparations,
            second_role_preparations=second_role_preparations,
        )

    async def edit_case(
        self,
        case_uuid: UUID,
        name: str | None = None,
        description: str | None = None,
        difficulty: CaseDifficulty | None = None,
        time_limit: int | None = None,
        system_prompt: str | None = None,
        goal: str | None = None,
        synopsis: str | None = None,
        first_role: str | None = None,
        second_role: str | None = None,
        first_role_preparations: str | None = None,
        second_role_preparations: str | None = None,
    ) -> Case:
        return await self._case_service.edit_case(
            case_uuid,
            name=name,
            description=description,
            difficulty=difficulty,
            time_limit=time_limit,
            system_prompt=system_prompt,
            goal=goal,
            synopsis=synopsis,
            first_role=first_role,
            second_role=second_role,
            first_role_preparations=first_role_preparations,
            second_role_preparations=second_role_preparations,
        )

    async def delete_case(self, case_uuid: UUID) -> bool:
        response = await delete_case(case_uuid=case_uuid)
        return response

    async def list_cases(self) -> list[Case]:
        return await self._case_service.list_cases()

    async def set_user_admin(self, user: User, code: str) -> User:
        if code != self._config.admin_code:
            raise ApiException(400, "invalid_code", "Invalid admin code")
        return await self.set_user_role(user, UserRole.ADMIN)

    async def set_user_role(self, user: User, role: UserRole) -> User:
        updated_user = await set_user_role(user, role)
        return updated_user


def get_admin_service(
    auth_service: AuthService = Depends(get_auth_service),
    case_service: CaseService = Depends(get_case_service),
) -> AdminService:
    return AdminService(config=settings, auth_service=auth_service, case_service=case_service)
