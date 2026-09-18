from uuid import UUID

from app.database.models import Chat, Message


async def create_message(*, chat: Chat, text: str, is_ai: bool) -> Message:
    last_message = await Message.filter(chat=chat).order_by("-sequence").first()
    sequence = last_message.sequence + 1 if last_message else 1
    return await Message.create(chat=chat, text=text, is_ai=is_ai, sequence=sequence)


async def get_messages_by_chat(chat: Chat) -> list[Message]:
    return await Message.filter(chat=chat).order_by("sequence")


async def get_message_by_uuid_for_chat(
    message_uuid: UUID | str, chat_uuid: UUID | str
) -> Message | None:
    return await Message.get_or_none(uuid=message_uuid, chat__uuid=chat_uuid)


async def delete_message(message: Message) -> None:
    await message.delete()


__all__ = [
    "create_message",
    "get_messages_by_chat",
    "get_message_by_uuid_for_chat",
    "delete_message",
]
