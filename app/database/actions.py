from typing import Optional
from uuid import UUID

from app.database.models import User, UserStatus


async def get_user_by_email(email: str) -> Optional[User]:
    return await User.get_or_none(email=email)


async def get_user_by_username(username: str) -> Optional[User]:
    return await User.get_or_none(username=username)


async def get_user_by_uuid(user_uuid: UUID | str) -> Optional[User]:
    return await User.get_or_none(uuid=user_uuid)


async def create_user(
    *,
    email: str,
    username: str,
    firstname: str,
    lastname: str,
    hashed_password: str,
) -> User:
    return await User.create(
        email=email,
        username=username,
        firstname=firstname,
        lastname=lastname,
        password=hashed_password,
        status=UserStatus.PENDING_ACTIVATION,
    )


async def activate_user(user: User) -> User:
    user.status = UserStatus.ACTIVE
    await user.save(update_fields=["status"])
    return user


async def set_password(user: User, hashed_password: str) -> User:
    user.password = hashed_password
    await user.save(update_fields=["password"])
    return user


__all__ = [
    "get_user_by_email",
    "get_user_by_username",
    "get_user_by_uuid",
    "create_user",
    "activate_user",
    "set_password",
]
