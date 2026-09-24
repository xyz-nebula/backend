from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.database.models import ChatStatus, UserStatus


class AuthRegisterRequest(BaseModel):
    email: EmailStr = Field(..., max_length=254)
    first_name: str = Field(..., min_length=1, max_length=64)
    last_name: str = Field(..., min_length=1, max_length=64)
    password: str = Field(..., min_length=8, max_length=128)


class AuthRegisterResponse(BaseModel):
    user_id: UUID
    status: UserStatus = UserStatus.PENDING_ACTIVATION


class AuthLoginRequest(BaseModel):
    email: EmailStr = Field(..., max_length=254)
    password: str = Field(..., min_length=8, max_length=128)
    totp_token: str | None = Field(default=None, pattern=r"^[0-9]{6}$")


class AuthActivationRequest(BaseModel):
    code: UUID


class AuthRefreshRequest(BaseModel):
    refresh_token: str


class AuthLogoutRequest(BaseModel):
    refresh_token: str


class AuthTokens(BaseModel):
    access_token: str
    refresh_token: str


class TotpEnrollResponse(BaseModel):
    secret: str
    otpauth_url: str


class TotpConfirmRequest(BaseModel):
    totp_token: str = Field(..., pattern=r"^[0-9]{6}$")


class TotpDisableRequest(BaseModel):
    password: str = Field(..., min_length=8, max_length=128)


class ChatCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)


class MessageResponse(BaseModel):
    uuid: UUID
    sequence: int
    is_ai: bool
    text: str
    created_at: datetime


class ChatResponse(BaseModel):
    uuid: UUID
    name: str
    status: ChatStatus
    created_at: datetime


class ChatListItem(BaseModel):
    uuid: UUID
    name: str


class ChatWithMessagesResponse(ChatResponse):
    messages: list[MessageResponse]


class ChatActivateRequest(BaseModel):
    uuid: UUID


class MessageCreateRequest(BaseModel):
    text: str = Field(..., min_length=1)
    is_ai: bool = False


__all__ = [
    "AuthRegisterRequest",
    "AuthRegisterResponse",
    "AuthLoginRequest",
    "AuthActivationRequest",
    "AuthRefreshRequest",
    "AuthLogoutRequest",
    "AuthTokens",
    "TotpEnrollResponse",
    "TotpConfirmRequest",
    "TotpDisableRequest",
    "ChatCreateRequest",
    "ChatListItem",
    "ChatResponse",
    "ChatWithMessagesResponse",
    "ChatActivateRequest",
    "MessageResponse",
    "MessageCreateRequest",
]
