import logging

import httpx

from app.config.config import Settings

logger = logging.getLogger(__name__)

_CONTRACT_HEADER = "X-Arena-Contract-Version"


class AIClientError(Exception):
    def __init__(self, status_code: int, code: str, message: str):
        self.status_code = status_code
        self.code = code
        self.message = message
        super().__init__(f"AI error {status_code} [{code}]: {message}")


class AIClient:
    def __init__(self, settings: Settings):
        self._client = httpx.AsyncClient(
            base_url=settings.ai_base_url,
            headers={
                "Authorization": f"Bearer {settings.ai_service_token}",
                _CONTRACT_HEADER: settings.ai_contract_version,
                "Content-Type": "application/json",
            },
            timeout=settings.ai_timeout_seconds,
        )

    async def evaluate(self, payload: dict) -> dict:
        return await self._post("/v2/evaluate", payload)

    async def _post(self, path: str, payload: dict) -> dict:
        try:
            response = await self._client.post(path, json=payload)
        except httpx.TimeoutException as exc:
            logger.error("AI request timed out path=%s", path)
            raise AIClientError(504, "timeout", "AI request timed out") from exc
        except httpx.RequestError as exc:
            logger.error("AI request failed path=%s error=%s", path, exc)
            raise AIClientError(502, "connection_error", str(exc)) from exc

        if response.status_code == 401:
            raise AIClientError(401, "unauthorized", "Invalid AI service token")
        if response.status_code == 409:
            body = self._try_json(response)
            raise AIClientError(409, body.get("code", "conflict"), body.get("message", ""))
        if response.status_code == 422:
            body = self._try_json(response)
            raise AIClientError(422, "invalid_request", str(body))
        if response.status_code != 200:
            raise AIClientError(
                response.status_code, "unexpected_status", f"HTTP {response.status_code}"
            )

        return response.json()

    @staticmethod
    def _try_json(response: httpx.Response) -> dict:
        try:
            return response.json()
        except Exception:
            return {}

    async def aclose(self) -> None:
        await self._client.aclose()


def get_ai_client(settings: Settings | None = None) -> AIClient:
    if settings is None:
        from app.config.config import settings as _settings

        settings = _settings
    return AIClient(settings)


__all__ = ["AIClient", "AIClientError", "get_ai_client"]
