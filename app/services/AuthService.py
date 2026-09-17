import secrets
from datetime import timedelta
from uuid import uuid4

import pyotp

from app.config.config import Settings, settings
from app.config.storage import ValkeyConfig
from app.database.actions import (
    activate_user,
    create_user,
    get_user_by_email,
    get_user_by_username,
    get_user_by_uuid,
)
from app.database.models import User, UserStatus
from app.exceptions import ApiException
from app.repository.base import BaseRepository
from app.repository.factory import RepositoryFactory
from app.services.JWTService import JWTService, get_jwt_service
from app.services.mailer import ActivationMailer, get_activation_mailer
from app.utils.password import hash_password, verify_password

_ACTIVATION_KEY_PREFIX = "activation:"
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
    ) -> User:
        if await get_user_by_email(email) is not None:
            raise ApiException(409, "email_taken", "Email is already registered", field="email")
        if await get_user_by_username(username) is not None:
            raise ApiException(409, "username_taken", "Username is already taken", field="username")

        user = await create_user(
            email=email,
            username=username,
            firstname=first_name,
            lastname=last_name,
            hashed_password=hash_password(password),
        )

        code = str(uuid4())
        await self._tokens.set(
            f"{_ACTIVATION_KEY_PREFIX}{code}",
            str(user.uuid),
            expiration=timedelta(minutes=self._config.activation_code_expire_minutes),
        )
        await self._mailer.send_activation_link(email=user.email, code=code)

        return user

    async def activate(self, code: str) -> tuple[str, str]:
        key = f"{_ACTIVATION_KEY_PREFIX}{code}"
        user_uuid = await self._tokens.get(key)
        if user_uuid is None:
            raise ApiException(404, "activation_code_not_found", "Activation code not found or expired")

        user = await get_user_by_uuid(user_uuid)
        if user is None:
            raise ApiException(404, "activation_code_not_found", "Activation code not found or expired")

        await activate_user(user)
        await self._tokens.delete(key)

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
            code = "account_suspended" if user.status == UserStatus.SUSPENDED else "account_not_activated"
            raise ApiException(403, code, "Account is not permitted to log in")

        if user.mfa_enabled:
            if not totp_token:
                raise ApiException(401, "mfa_required", "TOTP token is required")
            if not pyotp.TOTP(user.mfa_secret).verify(totp_token):
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


def get_auth_service() -> AuthService:
    return AuthService(
        config=settings,
        jwt_service=get_jwt_service(),
        mailer=get_activation_mailer(),
        token_repository=RepositoryFactory.create(ValkeyConfig()),
    )


__all__ = ["AuthService", "get_auth_service"]
