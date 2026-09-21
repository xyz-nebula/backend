from uuid import UUID

from app.database.models import User, UserStatus


async def require_user_by_email(email: str) -> User:
    return await User.get(email=email)


async def require_user_by_username(username: str) -> User:
    return await User.get(username=username)


async def get_user_by_email(email: str) -> User | None:
    return await User.get_or_none(email=email)


async def get_user_by_username(username: str) -> User | None:
    return await User.get_or_none(username=username)


async def get_user_by_uuid(user_uuid: UUID | str) -> User | None:
    return await User.get_or_none(uuid=user_uuid)


async def create_user(
    *,
    email: str,
    username: str,
    firstname: str,
    lastname: str,
    hashed_password: str,
    status: UserStatus = UserStatus.ACTIVE,
) -> User:
    return await User.create(
        email=email,
        username=username,
        firstname=firstname,
        lastname=lastname,
        password=hashed_password,
        status=status,
    )


async def update_user(user: User, **kwargs) -> User:
    for key, value in kwargs.items():
        setattr(user, key, value)
    await user.save()
    return user


async def activate_user(user: User) -> User:
    user.status = UserStatus.ACTIVE
    await user.save(update_fields=["status"])
    return user


async def check_user_activation_by_uuid(user_uuid: UUID | str) -> bool:
    user = await get_user_by_uuid(user_uuid)
    if user is None:
        return False
    if user.status == UserStatus.PENDING_ACTIVATION:
        return False
    elif user.status == UserStatus.ACTIVE:
        return True
    return False


async def check_user_activation_by_email(email: str) -> bool:
    user = await get_user_by_email(email)
    if user is None:
        return False
    return await check_user_activation_by_uuid(user.uuid)


async def check_user_activation_by_username(username: str) -> bool:
    user = await get_user_by_username(username)
    if user is None:
        return False
    return await check_user_activation_by_uuid(user.uuid)


async def set_password(user: User, hashed_password: str) -> User:
    user.password = hashed_password
    await user.save(update_fields=["password"])
    return user


async def set_mfa_secret(user: User, secret: str) -> User:
    user.mfa_secret = secret
    await user.save(update_fields=["mfa_secret"])
    return user


async def enable_mfa(user: User) -> User:
    user.mfa_enabled = True
    await user.save(update_fields=["mfa_enabled"])
    return user


async def disable_mfa(user: User) -> User:
    user.mfa_enabled = False
    user.mfa_secret = None
    await user.save(update_fields=["mfa_enabled", "mfa_secret"])
    return user


__all__ = [
    "get_user_by_email",
    "get_user_by_username",
    "get_user_by_uuid",
    "create_user",
    "activate_user",
    "set_password",
    "set_mfa_secret",
    "enable_mfa",
    "disable_mfa",
]
