import logging
from datetime import datetime, timedelta
from uuid import UUID

from app.database.models import Case, CaseDifficulty

logger = logging.getLogger(__name__)


async def create_case(
    name: str,
    description: str,
    category: str,
    difficulty: CaseDifficulty,
    time_limit: int,
    preparations: str,
) -> Case:
    case = await Case.create(
        name=name,
        description=description,
        category=category,
        difficulty=difficulty,
        time_limit=time_limit,
        preparations=preparations,
    )
    logger.info("Case created case_id=%s name=%s", case.uuid, name)
    return case


async def get_case(case_uuid: UUID) -> Case:
    logger.debug("Looking up case case_id=%s", case_uuid)
    return await Case.get(uuid=case_uuid)


async def get_all_cases() -> list[Case]:
    logger.debug("Listing all cases")
    return await Case.all().order_by("-created_at")


async def get_case_by_creation_date(date: datetime) -> list[Case]:
    """Return all cases created on the calendar day of `date`."""
    start = date.replace(hour=0, minute=0, second=0, microsecond=0)
    end = start + timedelta(days=1)
    logger.debug("Listing cases created between %s and %s", start, end)
    return await Case.filter(created_at__gte=start, created_at__lt=end).order_by("-created_at")


async def delete_case(case_uuid: UUID) -> bool:
    deleted = await Case.filter(uuid=case_uuid).delete()
    if deleted:
        logger.info("Case deleted case_id=%s", case_uuid)
    return bool(deleted)


async def edit_case(
    case_uuid: UUID,
    name: str | None = None,
    description: str | None = None,
    time_limit: int | None = None,
    preparations: str | None = None,
) -> Case:
    case = await Case.get(uuid=case_uuid)

    updates = {
        "name": name,
        "description": description,
        "time_limit": time_limit,
        "preparations": preparations,
    }
    changed = {field: value for field, value in updates.items() if value is not None}
    if changed:
        case.update_from_dict(changed)
        await case.save(update_fields=list(changed))
        logger.info("Case edited case_id=%s fields=%s", case_uuid, list(changed))
    return case


__all__ = [
    "create_case", 
    "get_case", 
    "get_all_cases", 
    "get_case_by_creation_date",
    "delete_case",
    "edit_case",
]