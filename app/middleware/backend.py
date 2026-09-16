from typing import Optional


class JWTAuthBackend:
    _instance: Optional["JWTAuthBackend"] = None
    