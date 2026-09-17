from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel


class ApiError(BaseModel):
    code: str
    message: str
    field: str | None = None


class ApiException(Exception):
    def __init__(self, status_code: int, code: str, message: str, field: str | None = None):
        self.status_code = status_code
        self.error = ApiError(code=code, message=message, field=field)


async def _api_exception_handler(request: Request, exc: ApiException) -> JSONResponse:
    return JSONResponse(status_code=exc.status_code, content=exc.error.model_dump())


async def _validation_exception_handler(
    request: Request, exc: RequestValidationError
) -> JSONResponse:
    first_error = exc.errors()[0]
    field = ".".join(str(part) for part in first_error["loc"][1:]) or None
    error = ApiError(code="validation_error", message=first_error["msg"], field=field)
    return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content=error.model_dump())


def register_exception_handlers(app: FastAPI) -> None:
    # FastAPI dispatches by the registered exception class, so these handlers only
    # ever run with the narrower type — pyright's ExceptionHandler stub just isn't
    # expressive enough to capture that.
    app.add_exception_handler(
        ApiException,
        _api_exception_handler,  # pyright: ignore[reportArgumentType]
    )
    app.add_exception_handler(
        RequestValidationError,
        _validation_exception_handler,  # pyright: ignore[reportArgumentType]
    )


__all__ = ["ApiError", "ApiException", "register_exception_handlers"]
