import logging
from uuid import UUID

from app.database.models import Chat, EvaluationJob, EvaluationJobStatus

logger = logging.getLogger(__name__)


async def create_evaluation_job(chat: Chat) -> EvaluationJob:
    job = await EvaluationJob.create(chat=chat)
    logger.info("EvaluationJob created job_id=%s chat_id=%s", job.uuid, chat.uuid)
    return job


async def get_evaluation_job_by_chat_uuid(chat_uuid: UUID | str) -> EvaluationJob | None:
    return await EvaluationJob.get_or_none(chat__uuid=chat_uuid)


async def get_evaluation_job_by_uuid(job_uuid: UUID | str) -> EvaluationJob | None:
    return await EvaluationJob.get_or_none(uuid=job_uuid)


async def update_evaluation_job(
    job: EvaluationJob,
    *,
    status: EvaluationJobStatus | None = None,
    result: dict | None = None,
    error: str | None = None,
) -> EvaluationJob:
    if status is not None:
        job.status = status
    if result is not None:
        job.result = result
    if error is not None:
        job.error = error
    await job.save()
    logger.info("EvaluationJob updated job_id=%s status=%s", job.uuid, job.status)
    return job


__all__ = [
    "create_evaluation_job",
    "get_evaluation_job_by_chat_uuid",
    "get_evaluation_job_by_uuid",
    "update_evaluation_job",
]
