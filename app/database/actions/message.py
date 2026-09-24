import logging
from uuid import UUID

from app.database.models import Chat, Message

logger = logging.getLogger(__name__)


async def create_message(*, chat: Chat, text: str, is_ai: bool) -> Message:
    last_message = await Message.filter(chat=chat).order_by("-sequence").first()
    sequence = last_message.sequence + 1 if last_message else 1
    message = await Message.create(chat=chat, text=text, is_ai=is_ai, sequence=sequence)
    logger.info(
        "Message created message_id=%s chat_id=%s sequence=%d is_ai=%s",
        message.uuid,
        chat.uuid,
        sequence,
        is_ai,
    )
    return message


async def get_messages_by_chat(chat: Chat) -> list[Message]:
    logger.debug("Listing messages for chat_id=%s", chat.uuid)
    return await Message.filter(chat=chat).order_by("sequence")


async def get_message_by_uuid_for_chat(
    message_uuid: UUID | str, chat_uuid: UUID | str
) -> Message | None:
    logger.debug("Looking up message message_id=%s chat_id=%s", message_uuid, chat_uuid)
    return await Message.get_or_none(uuid=message_uuid, chat__uuid=chat_uuid)


async def delete_message(message: Message) -> None:
    message_uuid = message.uuid
    await message.delete()
    logger.info("Message deleted message_id=%s", message_uuid)


__all__ = [
    "create_message",
    "get_messages_by_chat",
    "get_message_by_uuid_for_chat",
    "delete_message",
]
