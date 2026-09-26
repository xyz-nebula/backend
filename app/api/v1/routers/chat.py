from fastapi import APIRouter, Depends, status

from app.api.v1.routers.models import (
    ChatActivateRequest,
    ChatCreateRequest,
    ChatListItem,
    ChatResponse,
    ChatWithCaseResponse,
    ChatWithMessagesResponse,
    MessageCreateRequest,
    MessageResponse,
)
from app.dependencies import get_current_token_payload
from app.services.ChatService import ChatService, get_chat_service
from app.services.JWTService import TokenPayload

chat_router = APIRouter(
    prefix="/chats", tags=["Chat"], dependencies=[Depends(get_current_token_payload)]
)
message_router = APIRouter(
    prefix="/chats/{chat_uuid}/message",
    tags=["Chat"],
    dependencies=[Depends(get_current_token_payload)],
)


@chat_router.post("/", response_model=ChatResponse)
async def create_chat(
    body: ChatCreateRequest,
    payload: TokenPayload = Depends(get_current_token_payload),
    chat_service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    chat = await chat_service.create_chat(payload.sub, body.name, body.case_uuid)
    return ChatResponse(
        uuid=chat.uuid, name=chat.name, status=chat.status, created_at=chat.created_at
    )


@chat_router.get("/active", response_model=ChatWithCaseResponse)
async def get_active_chat(
    payload: TokenPayload = Depends(get_current_token_payload),
    chat_service: ChatService = Depends(get_chat_service),
) -> ChatResponse:
    chat = await chat_service.get_active_chat(payload.sub)
    return ChatWithCaseResponse(
        uuid=chat.uuid,
        name=chat.name,
        status=chat.status,
        created_at=chat.created_at,
        case=chat.case,
    )


@chat_router.put("/active", status_code=status.HTTP_204_NO_CONTENT)
async def activate_chat(
    body: ChatActivateRequest,
    payload: TokenPayload = Depends(get_current_token_payload),
    chat_service: ChatService = Depends(get_chat_service),
) -> None:
    await chat_service.activate_chat(payload.sub, str(body.uuid))


@chat_router.get("/{chat_uuid}", response_model=ChatWithMessagesResponse)
async def get_chat(
    chat_uuid: str,
    payload: TokenPayload = Depends(get_current_token_payload),
    chat_service: ChatService = Depends(get_chat_service),
) -> ChatWithMessagesResponse:
    # TODO: also return the case related to the chat
    chat, messages = await chat_service.get_chat(payload.sub, chat_uuid)
    return ChatWithMessagesResponse(
        uuid=chat.uuid,
        name=chat.name,
        status=chat.status,
        created_at=chat.created_at,
        messages=[
            MessageResponse(
                uuid=message.uuid,
                sequence=message.sequence,
                is_ai=message.is_ai,
                text=message.text,
                created_at=message.created_at,
            )
            for message in messages
        ],
    )


@chat_router.get("/", response_model=list[ChatListItem])
async def get_chats(
    payload: TokenPayload = Depends(get_current_token_payload),
    chat_service: ChatService = Depends(get_chat_service),
) -> list[ChatListItem]:
    chats = await chat_service.get_chats(payload.sub)
    return [ChatListItem(uuid=chat.uuid, name=chat.name) for chat in chats]


@chat_router.delete("/{chat_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_chat(
    chat_uuid: str,
    payload: TokenPayload = Depends(get_current_token_payload),
    chat_service: ChatService = Depends(get_chat_service),
) -> None:
    await chat_service.delete_chat(payload.sub, chat_uuid)


@message_router.post("/", response_model=MessageResponse)
async def post_message(
    chat_uuid: str,
    body: MessageCreateRequest,
    payload: TokenPayload = Depends(get_current_token_payload),
    chat_service: ChatService = Depends(get_chat_service),
) -> MessageResponse:
    message = await chat_service.post_message(payload.sub, chat_uuid, body.text, body.is_ai)
    return MessageResponse(
        uuid=message.uuid,
        sequence=message.sequence,
        is_ai=message.is_ai,
        text=message.text,
        created_at=message.created_at,
    )


@message_router.get("/{message_uuid}", response_model=MessageResponse)
async def get_message(
    chat_uuid: str,
    message_uuid: str,
    payload: TokenPayload = Depends(get_current_token_payload),
    chat_service: ChatService = Depends(get_chat_service),
) -> MessageResponse:
    message = await chat_service.get_message(payload.sub, chat_uuid, message_uuid)
    return MessageResponse(
        uuid=message.uuid,
        sequence=message.sequence,
        is_ai=message.is_ai,
        text=message.text,
        created_at=message.created_at,
    )


@message_router.delete("/{message_uuid}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_message(
    chat_uuid: str,
    message_uuid: str,
    payload: TokenPayload = Depends(get_current_token_payload),
    chat_service: ChatService = Depends(get_chat_service),
) -> None:
    await chat_service.delete_message(payload.sub, chat_uuid, message_uuid)


router = APIRouter()
router.include_router(chat_router)
router.include_router(message_router)
