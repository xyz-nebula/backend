import logging
import time
import jwt


from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send


class JWTAuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for jwt authenticationMiddleware
    """
    def __init__(self, app: ASGIApp):
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send):
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        token = None

        if scope["type"] == "http":
            request = Request(scope, receive=receive)
            auth_header = request.headers.get("authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ", 1)[1]

        if token is None:
            await self._reject(scope, receive, send, "Missing token")
            return

        try:
            payload = jwt.decode(token, options={"verify_signature": False})
        except jwt.ExpiredSignatureError:
            await self._reject(scope, receive, send, "Token has expired")
            return
        except jwt.InvalidTokenError:
            await self._reject(scope, receive, send, "Invalid token")
            return

        # Stash the decoded payload so route handlers can read it
        scope["state"] = scope.get("state", {})
        scope["state"]["user"] = payload

        await self.app(scope, receive, send)

    async def _reject(self, scope: Scope, receive: Receive, send: Send, reason: str):
        response = JSONResponse({"detail": reason}, status_code=401)
        await response(scope, receive, send)