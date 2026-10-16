import logging
from uuid import UUID

from fastapi import Depends

from app.database.actions.evaluation import (
    create_evaluation_job,
    get_evaluation_job_by_chat_uuid,
    get_evaluation_job_by_uuid,
    update_evaluation_job,
)
from app.database.actions.message import get_messages_by_chat
from app.database.models import Chat, ChatStatus, EvaluationJob, EvaluationJobStatus, SelectedRole
from app.exceptions import ApiException
from app.services.AIClient import AIClient, AIClientError, get_ai_client
from app.services.ChatService import ChatService, get_chat_service

logger = logging.getLogger(__name__)


class EvaluationService:
    def __init__(self, ai_client: AIClient, chat_service: ChatService):
        self._ai = ai_client
        self._chat_service = chat_service

    async def trigger(self, user_uuid: str, chat_uuid: str) -> EvaluationJob:
        chat = await self._chat_service._require_chat(user_uuid, chat_uuid)

        if chat.status != ChatStatus.ONGOING:
            raise ApiException(409, "chat_not_ongoing", "Chat is not in ongoing state")

        messages = await get_messages_by_chat(chat)
        if not messages:
            raise ApiException(422, "no_messages", "Chat has no messages to evaluate")

        existing = await get_evaluation_job_by_chat_uuid(chat.uuid)
        if existing is not None:
            raise ApiException(409, "already_evaluating", "Evaluation already exists for this chat")

        chat.status = ChatStatus.EVALUATING
        await chat.save()

        job = await create_evaluation_job(chat)
        logger.info("Evaluation triggered chat_id=%s job_id=%s", chat_uuid, job.uuid)
        return job

    async def run(self, job_uuid: UUID) -> None:
        job = await get_evaluation_job_by_uuid(job_uuid)
        if job is None:
            logger.error("EvaluationJob not found job_id=%s", job_uuid)
            return

        await job.fetch_related("chat__case")
        chat: Chat = job.chat
        case = chat.case

        await update_evaluation_job(job, status=EvaluationJobStatus.PROCESSING)

        messages = await get_messages_by_chat(chat)

        if chat.selected_role == SelectedRole.FIRST:
            role = case.first_role
            opponent_role = case.second_role
        else:
            role = case.second_role
            opponent_role = case.first_role

        payload: dict = {
            "role": role,
            "opponent_role": opponent_role,
            "case_description": case.description,
            "messages": [{"text": m.text, "is_ai": m.is_ai} for m in messages],
        }
        if chat.preparations:
            payload["preparations"] = chat.preparations

        try:
            result = await self._ai.evaluate(payload)
        except AIClientError as exc:
            logger.error("AI evaluate failed job_id=%s code=%s", job_uuid, exc.code)
            chat.status = ChatStatus.ONGOING
            await chat.save()
            await update_evaluation_job(job, status=EvaluationJobStatus.FAILED, error=str(exc))
            return

        chat.status = ChatStatus.EVALUATED
        await chat.save()
        await update_evaluation_job(job, status=EvaluationJobStatus.DONE, result=result)
        logger.info("Evaluation done job_id=%s", job_uuid)


def get_evaluation_service(
    ai_client: AIClient = Depends(get_ai_client),
    chat_service: ChatService = Depends(get_chat_service),
) -> EvaluationService:
    return EvaluationService(ai_client=ai_client, chat_service=chat_service)


__all__ = ["EvaluationService", "get_evaluation_service"]
