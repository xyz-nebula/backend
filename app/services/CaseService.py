import logging
from uuid import UUID

from tortoise.exceptions import DoesNotExist

from app.database.actions import create_case, edit_case, get_all_cases, get_case
from app.database.models import Case, CaseDifficulty
from app.exceptions import ApiException

logger = logging.getLogger(__name__)


class CaseService:
    """Case management. Authorization is the caller's job (see `get_current_admin`)."""

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
        return await create_case(
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
        try:
            return await edit_case(
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
        except DoesNotExist:
            raise ApiException(404, "case_not_found", "Case not found") from None

    async def get_case(self, case_uuid: UUID) -> Case:
        try:
            return await get_case(case_uuid)
        except DoesNotExist:
            raise ApiException(404, "case_not_found", "Case not found") from None

    async def list_cases(self) -> list[Case]:
        return await get_all_cases()


def get_case_service() -> CaseService:
    return CaseService()


__all__ = ["CaseService", "get_case_service"]
