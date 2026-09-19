from uuid import UUID

from app.database.models import Chat, User


async def create_chat(*, user: User, name: str) -> Chat:
    return await Chat.create(user=user, name=name)


async def get_chat_by_uuid_for_user(chat_uuid: UUID | str, user_uuid: UUID | str) -> Chat | None:
    return await Chat.get_or_none(uuid=chat_uuid, user__uuid=user_uuid)


async def delete_chat(chat: Chat) -> None:
    await chat.delete()


__all__ = [
    "create_chat",
    "get_chat_by_uuid_for_user",
    "delete_chat",
]
