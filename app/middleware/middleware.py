import logging
import time
import jwt

from starlette.middleware.base import BaseHTTPMiddleware


class JWTAuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for jwt authenticationMiddleware
    """