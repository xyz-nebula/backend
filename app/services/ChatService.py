from fastapi import Depends

from app.database.actions import (
    create_chat,
    create_message,
    delete_chat,
    delete_message,
    get_chat_by_uuid_for_user,
    get_message_by_uuid_for_chat,
    get_messages_by_chat,
    get_user_by_uuid,
    create_feedback,
    create_judgement
)
from app.database.models import Chat, Message, User
from app.exceptions import ApiException
from app.repository.base import BaseRepository
from app.repository.factory import get_token_repository

_ACTIVE_CHAT_KEY_PREFIX = "active_chat:"


class ChatService:
    def __init__(self, token_repository: BaseRepository):
        self._active_chats = token_repository

    async def create_chat(self, user_uuid: str, name: str) -> Chat:
        user = await self._require_user(user_uuid)
        return await create_chat(user=user, name=name)

    async def get_chat(self, user_uuid: str, chat_uuid: str) -> tuple[Chat, list[Message]]:
        chat = await self._require_chat(user_uuid, chat_uuid)
        messages = await get_messages_by_chat(chat)
        return chat, messages

    async def delete_chat(self, user_uuid: str, chat_uuid: str) -> None:
        chat = await self._require_chat(user_uuid, chat_uuid)
        await delete_chat(chat)

    async def activate_chat(self, user_uuid: str, chat_uuid: str) -> None:
        chat = await self._require_chat(user_uuid, chat_uuid)
        await self._active_chats.set(f"{_ACTIVE_CHAT_KEY_PREFIX}{user_uuid}", str(chat.uuid))

    async def get_active_chat(self, user_uuid: str) -> Chat:
        chat_uuid = await self._active_chats.get(f"{_ACTIVE_CHAT_KEY_PREFIX}{user_uuid}")
        if chat_uuid is None:
            raise ApiException(404, "no_active_chat", "No active chat is set")
        return await self._require_chat(user_uuid, chat_uuid)

    async def post_message(self, user_uuid: str, chat_uuid: str, text: str, is_ai: bool) -> Message:
        chat = await self._require_chat(user_uuid, chat_uuid)
        return await create_message(chat=chat, text=text, is_ai=is_ai)

    async def get_message(self, user_uuid: str, chat_uuid: str, message_uuid: str) -> Message:
        chat = await self._require_chat(user_uuid, chat_uuid)
        message = await get_message_by_uuid_for_chat(message_uuid, chat.uuid)
        if message is None:
            raise ApiException(404, "message_not_found", "Message not found")
        return message

    async def delete_message(self, user_uuid: str, chat_uuid: str, message_uuid: str) -> None:
        message = await self.get_message(user_uuid, chat_uuid, message_uuid)
        await delete_message(message)

    async def create_feedback(self, session_uuid: str, text: str):
        return await create_feedback(session_uuid=session_uuid, text=text)

    async def create_judgement(self, session_uuid: str, text: str):
        return await create_judgement(session_uuid=session_uuid, text=text)

    async def _require_user(self, user_uuid: str) -> User:
        user = await get_user_by_uuid(user_uuid)
        if user is None:
            raise ApiException(401, "invalid_token", "User no longer exists")
        return user

    async def _require_chat(self, user_uuid: str, chat_uuid: str) -> Chat:
        chat = await get_chat_by_uuid_for_user(chat_uuid, user_uuid)
        if chat is None:
            raise ApiException(404, "chat_not_found", "Chat not found")
        return chat


def get_chat_service(
    token_repository: BaseRepository = Depends(get_token_repository),
) -> ChatService:
    return ChatService(token_repository=token_repository)


__all__ = ["ChatService", "get_chat_service"]
