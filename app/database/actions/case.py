import logging
from uuid import UUID
from typing import Optional
from datetime import datetime

from app.database.models import Case, CaseDifficulty, Chat, ChatStatus

logger = logging.getLogger(__name__)


async def create_case(
    name: str,
    description: str,
    category: str,
    difficulty: CaseDifficulty,
    time_limit: int,
    preparations: str
):...


async def get_case(case_uuid: UUID):...


async def get_all_cases():...


async def get_case_by_creation_date(date: datetime):...


async def delete_case(case_uuid: UUID):...


async def edit_case(
    case_uuid: UUID,
    name: Optional[str],
    description: Optional[str],
    time_limit: Optional[str],
    preparations: Optional[str]
):...