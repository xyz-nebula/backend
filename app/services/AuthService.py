import json
import secrets
from datetime import timedelta
from uuid import UUID, uuid4

import pyotp
from fastapi import Depends
from tortoise.exceptions import IntegrityError

from app.config.config import Settings, settings
from app.database.actions import (
    create_user,
    disable_mfa,
    enable_mfa,
    get_user_by_email,
    get_user_by_username,
    get_user_by_uuid,
    set_mfa_secret,
)
from app.database.models import User, UserStatus
from app.exceptions import ApiException
from app.repository.base import BaseRepository
from app.repository.factory import get_token_repository
from app.services.JWTService import JWTService, get_jwt_service
from app.services.mailer import ActivationMailer, get_activation_mailer
from app.utils.password import hash_password, verify_password

_ACTIVATION_KEY_PREFIX = "activation:"
_PENDING_EMAIL_KEY_PREFIX = "pending_email:"
_PENDING_USERNAME_KEY_PREFIX = "pending_username:"
_REFRESH_KEY_PREFIX = "refresh:"


class AuthService:
    def __init__(
        self,
        config: Settings,
        jwt_service: JWTService,
        mailer: ActivationMailer,
        token_repository: BaseRepository,
    ):
        self._config = config
        self._jwt_service = jwt_service
        self._mailer = mailer
        self._tokens = token_repository

    async def register(
        self,
        *,
        email: str,
        username: str,
        first_name: str,
        last_name: str,
        password: str,
    ) -> UUID:
        if await get_user_by_email(email):
            raise ApiException(409, "email_taken", "Email is already registered", field="email")
        if await get_user_by_username(username):
            raise ApiException(409, "username_taken", "Username is already taken", field="username")

        email_code = await self._tokens.get(f"{_PENDING_EMAIL_KEY_PREFIX}{email}")
        username_code = await self._tokens.get(f"{_PENDING_USERNAME_KEY_PREFIX}{username}")
        if email_code and email_code == username_code:
            # Same (email, username) pair: wipe the old pending so this acts as a resend
            await self._cleanup_pending(email_code)
        elif email_code:
            raise ApiException(409, "email_taken", "Email is already registered", field="email")
        elif username_code:
            raise ApiException(409, "username_taken", "Username is already taken", field="username")

        ttl = timedelta(minutes=self._config.activation_code_expire_minutes)
        code = str(uuid4())
        user_id = uuid4()
        pending_data = json.dumps(
            {
                "user_id": str(user_id),
                "email": email,
                "username": username,
                "first_name": first_name,
                "last_name": last_name,
                "hashed_password": hash_password(password),
            }
        )
        await self._tokens.set(f"{_ACTIVATION_KEY_PREFIX}{code}", pending_data, expiration=ttl)
        await self._tokens.set(f"{_PENDING_EMAIL_KEY_PREFIX}{email}", code, expiration=ttl)
        await self._tokens.set(f"{_PENDING_USERNAME_KEY_PREFIX}{username}", code, expiration=ttl)
        await self._mailer.send_activation_link(email=email, code=code)
        return user_id

    async def _cleanup_pending(self, code: str) -> None:
        raw = await self._tokens.get(f"{_ACTIVATION_KEY_PREFIX}{code}")
        if raw:
            data = json.loads(raw)
            await self._tokens.delete(f"{_PENDING_EMAIL_KEY_PREFIX}{data['email']}")
            await self._tokens.delete(f"{_PENDING_USERNAME_KEY_PREFIX}{data['username']}")
            await self._tokens.delete(f"{_ACTIVATION_KEY_PREFIX}{code}")

    async def activate(self, code: str) -> tuple[str, str]:
        key = f"{_ACTIVATION_KEY_PREFIX}{code}"
        raw = await self._tokens.get(key)
        if raw is None:
            raise ApiException(
                404, "activation_code_not_found", "Activation code not found or expired"
            )

        data = json.loads(raw)
        try:
            user = await create_user(
                user_id=UUID(data["user_id"]),
                email=data["email"],
                username=data["username"],
                firstname=data["first_name"],
                lastname=data["last_name"],
                hashed_password=data["hashed_password"],
                status=UserStatus.ACTIVE,
            )
        except IntegrityError:
            raise ApiException(
                409, "account_conflict", "Email or username is already registered"
            ) from None
        await self._tokens.delete(key)
        await self._tokens.delete(f"{_PENDING_EMAIL_KEY_PREFIX}{data['email']}")
        await self._tokens.delete(f"{_PENDING_USERNAME_KEY_PREFIX}{data['username']}")

        return await self._issue_tokens(user)

    async def login(
        self,
        *,
        email: str,
        password: str,
        totp_token: str | None,
    ) -> tuple[str, str]:
        user = await get_user_by_email(email)
        if user is None or not verify_password(password, user.password):
            raise ApiException(401, "invalid_credentials", "Invalid email or password")

        if user.status != UserStatus.ACTIVE:
            code = (
                "account_suspended"
                if user.status == UserStatus.SUSPENDED
                else "account_not_activated"
            )
            raise ApiException(403, code, "Account is not permitted to log in")

        if user.mfa_enabled:
            if not totp_token:
                raise ApiException(401, "mfa_required", "TOTP token is required")
            assert user.mfa_secret is not None, "mfa_enabled implies mfa_secret is set"
            if not pyotp.TOTP(user.mfa_secret).verify(totp_token, valid_window=1):
                raise ApiException(401, "invalid_credentials", "Invalid TOTP token")

        return await self._issue_tokens(user)

    async def refresh(self, refresh_token: str) -> tuple[str, str]:
        key = f"{_REFRESH_KEY_PREFIX}{refresh_token}"
        user_uuid = await self._tokens.get(key)
        if user_uuid is None:
            raise ApiException(401, "invalid_token", "Refresh token is invalid or expired")

        user = await get_user_by_uuid(user_uuid)
        if user is None:
            raise ApiException(401, "invalid_token", "Refresh token is invalid or expired")

        await self._tokens.delete(key)

        return await self._issue_tokens(user)

    async def logout(self, refresh_token: str) -> None:
        await self._tokens.delete(f"{_REFRESH_KEY_PREFIX}{refresh_token}")

    async def enroll_totp(self, user_uuid: str) -> tuple[str, str]:
        user = await self._require_user(user_uuid)
        if user.mfa_enabled:
            raise ApiException(409, "mfa_already_enabled", "TOTP is already enabled")

        secret = pyotp.random_base32()
        await set_mfa_secret(user, secret)
        otpauth_url = pyotp.TOTP(secret).provisioning_uri(name=user.email, issuer_name="Nebula")
        return secret, otpauth_url

    async def confirm_totp(self, user_uuid: str, totp_token: str) -> None:
        user = await self._require_user(user_uuid)
        if user.mfa_enabled:
            raise ApiException(409, "mfa_already_enabled", "TOTP is already enabled")
        if not user.mfa_secret:
            raise ApiException(400, "totp_not_enrolled", "Start TOTP enrollment first")
        if not pyotp.TOTP(user.mfa_secret).verify(totp_token, valid_window=1):
            raise ApiException(401, "invalid_totp_token", "Invalid TOTP token")

        await enable_mfa(user)

    async def disable_totp(self, user_uuid: str, password: str) -> None:
        user = await self._require_user(user_uuid)
        if not user.mfa_enabled:
            raise ApiException(409, "mfa_not_enabled", "TOTP is not enabled")
        if not verify_password(password, user.password):
            raise ApiException(401, "invalid_credentials", "Invalid password")

        await disable_mfa(user)

    async def _require_user(self, user_uuid: str) -> User:
        user = await get_user_by_uuid(user_uuid)
        if user is None:
            raise ApiException(401, "invalid_token", "User no longer exists")
        return user

    async def _issue_tokens(self, user: User) -> tuple[str, str]:
        access_token = self._jwt_service.encode(
            sub=str(user.uuid),
            expires_delta=timedelta(minutes=self._config.jwt_expire_minutes),
        )
        refresh_token = secrets.token_urlsafe(32)
        await self._tokens.set(
            f"{_REFRESH_KEY_PREFIX}{refresh_token}",
            str(user.uuid),
            expiration=timedelta(days=self._config.refresh_token_expire_days),
        )
        return access_token, refresh_token


def get_auth_service(
    jwt_service: JWTService = Depends(get_jwt_service),
    mailer: ActivationMailer = Depends(get_activation_mailer),
    token_repository: BaseRepository = Depends(get_token_repository),
) -> AuthService:
    return AuthService(
        config=settings,
        jwt_service=jwt_service,
        mailer=mailer,
        token_repository=token_repository,
    )


__all__ = ["AuthService", "get_auth_service"]
