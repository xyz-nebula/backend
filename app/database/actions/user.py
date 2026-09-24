import logging
from uuid import UUID

from app.database.models import User, UserStatus

logger = logging.getLogger(__name__)


async def require_user_by_email(email: str) -> User:
    logger.debug("Fetching required user by email=%s", email)
    return await User.get(email=email)


async def get_user_by_email(email: str) -> User | None:
    logger.debug("Looking up user by email=%s", email)
    return await User.get_or_none(email=email)


async def get_user_by_uuid(user_uuid: UUID | str) -> User | None:
    logger.debug("Looking up user by uuid=%s", user_uuid)
    return await User.get_or_none(uuid=user_uuid)


async def create_user(
    *,
    email: str,
    firstname: str,
    lastname: str,
    hashed_password: str,
    status: UserStatus = UserStatus.ACTIVE,
    user_id: UUID | None = None,
) -> User:
    user = await User.create(
        **({"uuid": user_id} if user_id else {}),
        email=email,
        firstname=firstname,
        lastname=lastname,
        password=hashed_password,
        status=status,
    )
    logger.info("User created user_id=%s email=%s status=%s", user.uuid, email, status)
    return user


async def update_user(user: User, **kwargs) -> User:
    fields = ", ".join(kwargs.keys())
    for key, value in kwargs.items():
        setattr(user, key, value)
    await user.save()
    logger.info("User updated user_id=%s fields=[%s]", user.uuid, fields)
    return user


async def activate_user(user: User) -> User:
    user.status = UserStatus.ACTIVE
    await user.save(update_fields=["status"])
    logger.info("User activated user_id=%s", user.uuid)
    return user


async def check_user_activation_by_uuid(user_uuid: UUID | str) -> bool:
    user = await get_user_by_uuid(user_uuid)
    if user is None:
        logger.debug("Activation check: user not found uuid=%s", user_uuid)
        return False
    if user.status == UserStatus.PENDING_ACTIVATION:
        logger.debug("Activation check: pending uuid=%s", user_uuid)
        return False
    elif user.status == UserStatus.ACTIVE:
        return True
    return False


async def check_user_activation_by_email(email: str) -> bool:
    user = await get_user_by_email(email)
    if user is None:
        return False
    return await check_user_activation_by_uuid(user.uuid)


async def set_password(user: User, hashed_password: str) -> User:
    user.password = hashed_password
    await user.save(update_fields=["password"])
    logger.info("Password updated user_id=%s", user.uuid)
    return user


async def set_mfa_secret(user: User, secret: str) -> User:
    user.mfa_secret = secret
    await user.save(update_fields=["mfa_secret"])
    logger.info("MFA secret set user_id=%s", user.uuid)
    return user


async def enable_mfa(user: User) -> User:
    user.mfa_enabled = True
    await user.save(update_fields=["mfa_enabled"])
    logger.info("MFA enabled user_id=%s", user.uuid)
    return user


async def disable_mfa(user: User) -> User:
    user.mfa_enabled = False
    user.mfa_secret = None
    await user.save(update_fields=["mfa_enabled", "mfa_secret"])
    logger.info("MFA disabled user_id=%s", user.uuid)
    return user


__all__ = [
    "get_user_by_email",
    "get_user_by_uuid",
    "create_user",
    "activate_user",
    "set_password",
    "set_mfa_secret",
    "enable_mfa",
    "disable_mfa",
]
