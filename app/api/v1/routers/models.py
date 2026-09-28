from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.database.models import (
    CaseDifficulty,
    ChatStatus,
    EvaluationJobStatus,
    SelectedRole,
    UserStatus,
)


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
    selected_role: SelectedRole
    preparations: str = Field(default="", max_length=10000)


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
    goal: str
    synopsis: str
    first_role: str
    second_role: str
    first_role_preparations: str
    second_role_preparations: str
    system_prompt: str


class CaseCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: str = Field(..., min_length=1)
    category: str = Field(..., min_length=1, max_length=100)
    difficulty: CaseDifficulty
    time_limit: int = Field(..., gt=0)
    system_prompt: str = Field(..., min_length=1)
    goal: str = Field(..., min_length=1)
    synopsis: str = Field(..., min_length=1)
    first_role: str = Field(..., min_length=1)
    second_role: str = Field(..., min_length=1)
    first_role_preparations: str
    second_role_preparations: str


class CaseEditRequest(BaseModel):
    name: str | None = Field(None, min_length=1, max_length=100)
    description: str | None = Field(None, min_length=1)
    difficulty: CaseDifficulty | None = None
    time_limit: int | None = Field(None, gt=0)
    system_prompt: str | None = Field(None, min_length=1)
    goal: str | None = Field(None, min_length=1)
    synopsis: str | None = Field(None, min_length=1)
    first_role: str | None = Field(None, min_length=1)
    second_role: str | None = Field(None, min_length=1)
    first_role_preparations: str | None = None
    second_role_preparations: str | None = None


class ChatResponse(BaseModel):
    uuid: UUID
    name: str
    status: ChatStatus
    preparations: str
    selected_role: SelectedRole
    created_at: datetime


class ChatListItem(BaseModel):
    uuid: UUID
    name: str
    selected_role: SelectedRole


class ChatWithCaseResponse(ChatResponse):
    case: CaseResponse


class ChatWithMessagesResponse(ChatWithCaseResponse):
    messages: list[MessageResponse]


class ChatActivateRequest(BaseModel):
    uuid: UUID


class MessageCreateRequest(BaseModel):
    text: str = Field(..., min_length=1)
    is_ai: bool = False


# ── Arena AI evaluation result schema (contract 2.0.0-rc.1) ──────────────────


class AIEvidence(BaseModel):
    message_index: int
    is_ai: bool
    quote: str


class AIOutcomeAssessment(BaseModel):
    kind: str  # agreement | partial_agreement | deferred | no_agreement | not_assessable
    summary: str
    agreed_terms: list[str]
    open_points: list[str]
    next_step: str | None
    evidence: list[AIEvidence]


class AIOutcome(BaseModel):
    basis: str
    status: str  # ready | failed
    assessment: AIOutcomeAssessment | None
    error_code: str | None


class AIVerdict(BaseModel):
    college: str
    choice: str  # player | opponent
    decisive_criterion: str
    evidence: AIEvidence
    observation: str
    effect: str
    comparison: str


class AIJudgeSlot(BaseModel):
    college: str
    status: str  # ready | failed
    verdict: AIVerdict | None
    error_code: str | None


class AICoachingPoint(BaseModel):
    evidence: AIEvidence
    action: str
    situation_change: str
    consequence: str


class AIPlanItem(BaseModel):
    preparation_text: str
    status: str  # followed | adapted | not_observed
    evidence: AIEvidence | None
    observation: str


class AIPlanVsReality(BaseModel):
    summary: str
    items: list[AIPlanItem]


class AIGoalAssessment(BaseModel):
    status: str  # achieved | partially_achieved | not_achieved | not_assessable
    goal_text: str | None
    explanation: str
    evidence: list[AIEvidence]


class AITrainerFeedbackContent(BaseModel):
    summary: str
    strengths: list[AICoachingPoint]
    mistakes: list[AICoachingPoint]
    missed_opportunities: list[AICoachingPoint]
    next_try: list[str]
    plan_vs_reality: AIPlanVsReality | None
    goal_assessment: AIGoalAssessment


class AITrainerFeedback(BaseModel):
    status: str  # ready | failed
    feedback: AITrainerFeedbackContent | None
    error_code: str | None


class AIEvaluationResult(BaseModel):
    contract_version: str
    outcome: AIOutcome
    judge_verdicts: list[AIJudgeSlot]
    trainer_feedback: AITrainerFeedback


# ─────────────────────────────────────────────────────────────────────────────


class EvaluateTriggerResponse(BaseModel):
    job_uuid: UUID
    status: EvaluationJobStatus


class EvaluationResultResponse(BaseModel):
    status: EvaluationJobStatus
    result: AIEvaluationResult | None
    error: str | None


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
    "CaseCreateRequest",
    "CaseEditRequest",
    "ChatWithCaseResponse",
    "AdminRegisterRequest",
    "EvaluateTriggerResponse",
    "EvaluationResultResponse",
    "AIEvaluationResult",
    "AIOutcome",
    "AIJudgeSlot",
    "AITrainerFeedback",
    "AIEvidence",
]
