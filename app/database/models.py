import uuid
from enum import StrEnum

from tortoise import fields
from tortoise.models import Model


class UserStatus(StrEnum):
    PENDING_ACTIVATION = "pending_activation"
    ACTIVE = "active"
    SUSPENDED = "suspended"


class UserRole(StrEnum):
    USER = "user"
    ADMIN = "admin"


class CaseDifficulty(StrEnum):
    EASY = "easy"
    MODERATE = "moderate"
    HARD = "hard"
    INSANE = "insane"


class User(Model):
    id = fields.IntField(pk=True)
    uuid = fields.UUIDField(unique=True, default=uuid.uuid4)
    created_at = fields.DatetimeField(auto_now_add=True)

    firstname = fields.CharField(max_length=100)
    lastname = fields.CharField(max_length=100)
    email = fields.CharField(max_length=254, unique=True)
    password = fields.CharField(max_length=60)

    status = fields.CharEnumField(UserStatus, default=UserStatus.PENDING_ACTIVATION)
    role = fields.CharEnumField(UserRole, default=UserRole.USER)
    mfa_enabled = fields.BooleanField(default=False)
    mfa_secret = fields.CharField(max_length=32, null=True)

    class Meta:
        table = "user"

    def __str__(self) -> str:
        return f"User({self.uuid}, {self.email})"


class ChatStatus(StrEnum):
    VICTORY = "victory"
    DEFEAT = "defeat"
    ONGOING = "ongoing"


class Chat(Model):
    id = fields.IntField(pk=True)
    uuid = fields.UUIDField(unique=True, default=uuid.uuid4)
    created_at = fields.DatetimeField(auto_now_add=True)

    name = fields.CharField(max_length=100)
    user = fields.ForeignKeyField("models.User", related_name="chats")
    case = fields.ForeignKeyField("models.Case", related_name="chats")
    status = fields.CharEnumField(ChatStatus, default=ChatStatus.ONGOING)

    class Meta:
        table = "chat"

    def __str__(self) -> str:
        return f"Chat({self.uuid}, {self.name})"


class Case(Model):
    id = fields.IntField(pk=True)
    uuid = fields.UUIDField(unique=True, default=uuid.uuid4)
    created_at = fields.DatetimeField(auto_now_add=True)
    name = fields.CharField(max_length=100)
    description = fields.TextField()
    category = fields.CharField(max_length=100)
    difficulty = fields.CharField(max_length=100)
    time_limit = fields.IntField()
    preparations = fields.TextField()

    class Meta:
        table = "case"

    def __str__(self) -> str:
        return f"Case({self.uuid}, {self.name})"


class Feedback(Model):
    """
    Feedback:
        - id (INT, PK)
        - uuid (UUID, UK)
        - created_at (DATETIME)
        - session_uuid (UUID, FK)
        - text (TEXT)
    """

    id = fields.IntField(pk=True)
    uuid = fields.UUIDField(unique=True, default=uuid.uuid4)
    created_at = fields.DatetimeField(auto_now_add=True)

    session_uuid = fields.UUIDField()
    text = fields.TextField()

    class Meta:
        table = "feedback"

    def __str__(self) -> str:
        return f"Feedback({self.uuid}, {self.text[:20]}...)"


class Judgement(Model):
    """
    Judgement:
        - id (INT, PK)
        - uuid (UUID, UK)
        - created_at (DATETIME)
        - session_uuid (UUID, FK)
        - text (TEXT)
    """

    id = fields.IntField(pk=True)
    uuid = fields.UUIDField(unique=True, default=uuid.uuid4)
    created_at = fields.DatetimeField(auto_now_add=True)

    session_uuid = fields.UUIDField()
    text = fields.TextField()

    class Meta:
        table = "judgement"

    def __str__(self) -> str:
        return f"Judgement({self.uuid}, {self.text[:20]}...)"


class Message(Model):
    id = fields.IntField(pk=True)
    uuid = fields.UUIDField(unique=True, default=uuid.uuid4)
    created_at = fields.DatetimeField(auto_now_add=True)
    sequence = fields.IntField()
    is_ai = fields.BooleanField(default=False)

    text = fields.TextField()
    chat = fields.ForeignKeyField("models.Chat", related_name="messages")

    class Meta:
        table = "message"

    def __str__(self) -> str:
        return f"Message({self.uuid}, {'AI' if self.is_ai else 'User'}: {self.text[:20]}...)"


__all__ = ["User", "UserStatus", "Chat", "ChatStatus", "Message", "Case", "CaseDifficulty"]
