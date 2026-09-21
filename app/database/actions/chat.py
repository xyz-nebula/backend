from uuid import UUID

from app.database.models import Chat, Feedback, Judgement, User


async def create_chat(*, user: User, name: str) -> Chat:
    return await Chat.create(user=user, name=name)


async def get_chat_by_uuid_for_user(chat_uuid: UUID | str, user_uuid: UUID | str) -> Chat | None:
    return await Chat.get_or_none(uuid=chat_uuid, user__uuid=user_uuid)


async def delete_chat(chat: Chat) -> None:
    await chat.delete()


async def create_feedback(*, session_uuid: UUID | str, text: str) -> Feedback:
    return await Feedback.create(session_uuid=session_uuid, text=text)


async def create_judgement(*, session_uuid: UUID | str, text: str) -> Judgement:
    return await Judgement.create(session_uuid=session_uuid, text=text)


__all__ = [
    "create_chat",
    "get_chat_by_uuid_for_user",
    "delete_chat",
    "create_feedback",
    "create_judgement",
]
