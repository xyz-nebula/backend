from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.types import ASGIApp, Receive, Scope, Send

from app.services.JWTService import get_jwt_service


class JWTAuthenticationMiddleware(BaseHTTPMiddleware):
    """
    Middleware for jwt authenticationMiddleware
    """
    def __init__(self, app: ASGIApp):
        super().__init__(app)
        self.jwt_service = get_jwt_service()

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
            payload = self.jwt_service.decode(token)
        except ValueError as exc:
            await self._reject(scope, receive, send, str(exc))
            return

        # Stash the decoded payload so route handlers can read it
        scope["state"] = scope.get("state", {})
        scope["state"]["user"] = payload.model_dump()

        await self.app(scope, receive, send)

    async def _reject(self, scope: Scope, receive: Receive, send: Send, reason: str):
        response = JSONResponse({"detail": reason}, status_code=401)
        await response(scope, receive, send)