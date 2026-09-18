import bcrypt

# bcrypt only considers the first 72 bytes of the input.
_MAX_PASSWORD_BYTES = 72


def _truncate(plain: str) -> bytes:
    return plain.encode("utf-8")[:_MAX_PASSWORD_BYTES]


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(_truncate(plain), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain: str, hashed: str) -> bool:
    return bcrypt.checkpw(_truncate(plain), hashed.encode("utf-8"))


__all__ = ["hash_password", "verify_password"]
