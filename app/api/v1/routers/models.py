from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.database.models import CaseDifficulty, ChatStatus, UserStatus


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
    case_uuid: UUID


class MessageResponse(BaseModel):
    uuid: UUID
    sequence: int
    is_ai: bool
    text: str
    created_at: datetime


class CaseResponse(BaseModel):
    uuid: UUID
    created_at: datetime
    name: str
    description: str
    category: str
    difficulty: str
    time_limit: int
    preparations: str
    goal: str
    synopsis: str
    first_role: str
    second_role: str


class AdminCaseResponse(CaseResponse):
    system_prompt: str


class CaseCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1, max_length=100)
    difficulty: CaseDifficulty
    time_limit: int = Field(..., gt=0)
    preparations: str
    system_prompt: str = Field(..., min_length=1)
    goal: str = Field(..., min_length=1)
    synopsis: str = Field(..., min_length=1)
    first_role: str = Field(..., min_length=1)
    second_role: str = Field(..., min_length=1)


class CaseEditRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, min_length=1)
    time_limit: int | None = Field(None, gt=0)
    preparations: str | None = None
    system_prompt: str | None = Field(None, min_length=1)
    goal: str | None = Field(None, min_length=1)
    synopsis: str | None = Field(None, min_length=1)
    first_role: str | None = Field(None, min_length=1)
    second_role: str | None = Field(None, min_length=1)


class ChatResponse(BaseModel):
    uuid: UUID
    name: str
    status: ChatStatus
    created_at: datetime


class ChatListItem(BaseModel):
    uuid: UUID
    name: str


class ChatWithCaseResponse(ChatResponse):
    case: CaseResponse


class ChatWithMessagesResponse(ChatWithCaseResponse):
    messages: list[MessageResponse]


class ChatActivateRequest(BaseModel):
    uuid: UUID


class MessageCreateRequest(BaseModel):
    text: str = Field(..., min_length=1)
    is_ai: bool = False


class AdminRegisterRequest(BaseModel):
    code: str = Field(...)


__all__ = [
    "AuthRegisterRequest",
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
    "CaseResponse",
    "AdminCaseResponse",
    "CaseCreateRequest",
    "CaseEditRequest",
    "ChatWithCaseResponse",
    "AdminRegisterRequest",
]
