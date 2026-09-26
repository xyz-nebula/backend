import logging
from uuid import UUID

from app.database.models import Case, Chat, Feedback, Judgement, User

logger = logging.getLogger(__name__)


async def create_chat(*, user: User, case: Case, name: str) -> Chat:
    chat = await Chat.create(user=user, case=case, name=name)
    logger.info(
        "Chat created chat_id=%s user_id=%s case_id=%s name=%s",
        chat.uuid,
        user.uuid,
        case.uuid,
        name,
    )
    return chat


async def get_chat_by_uuid_for_user(chat_uuid: UUID | str, user_uuid: UUID | str) -> Chat | None:
    logger.debug("Looking up chat chat_id=%s user_id=%s", chat_uuid, user_uuid)
    return await Chat.get_or_none(uuid=chat_uuid, user__uuid=user_uuid)


async def get_chats_by_user(user_uuid: UUID | str) -> list[Chat]:
    logger.debug("Listing chats for user_id=%s", user_uuid)
    return await Chat.filter(user__uuid=user_uuid).order_by("-created_at")


async def delete_chat(chat: Chat) -> None:
    chat_uuid = chat.uuid
    await chat.delete()
    logger.info("Chat deleted chat_id=%s", chat_uuid)


async def create_feedback(*, session_uuid: UUID | str, text: str) -> Feedback:
    feedback = await Feedback.create(session_uuid=session_uuid, text=text)
    logger.info("Feedback created feedback_id=%s session_id=%s", feedback.uuid, session_uuid)
    return feedback


async def create_judgement(*, session_uuid: UUID | str, text: str) -> Judgement:
    judgement = await Judgement.create(session_uuid=session_uuid, text=text)
    logger.info("Judgement created judgement_id=%s session_id=%s", judgement.uuid, session_uuid)
    return judgement


__all__ = [
    "create_chat",
    "get_chat_by_uuid_for_user",
    "get_chats_by_user",
    "delete_chat",
    "create_feedback",
    "create_judgement",
]
