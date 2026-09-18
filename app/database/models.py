import uuid
from enum import StrEnum

from tortoise import fields
from tortoise.models import Model


class UserStatus(StrEnum):
    PENDING_ACTIVATION = "pending_activation"
    ACTIVE = "active"
    SUSPENDED = "suspended"


class User(Model):
    id = fields.IntField(pk=True)
    uuid = fields.UUIDField(unique=True, default=uuid.uuid4)
    created_at = fields.DatetimeField(auto_now_add=True)

    username = fields.CharField(max_length=100, unique=True)
    firstname = fields.CharField(max_length=100)
    lastname = fields.CharField(max_length=100)
    email = fields.CharField(max_length=254, unique=True)
    password = fields.CharField(max_length=60)

    status = fields.CharEnumField(UserStatus, default=UserStatus.PENDING_ACTIVATION)
    mfa_enabled = fields.BooleanField(default=False)
    mfa_secret = fields.CharField(max_length=32, null=True)

    class Meta:
        table = "user"

    def __str__(self) -> str:
        return f"User({self.uuid}, {self.email})"


__all__ = ["User", "UserStatus"]
