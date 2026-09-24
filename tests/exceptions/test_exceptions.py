from fastapi import Request
from fastapi.exceptions import RequestValidationError

from app.exceptions import ApiException, _validation_exception_handler


def test_api_exception_builds_error_envelope():
    exc = ApiException(409, "email_taken", "Email is already registered", field="email")
    assert exc.status_code == 409
    assert exc.error.model_dump() == {
        "code": "email_taken",
        "message": "Email is already registered",
        "field": "email",
    }


def test_api_exception_field_defaults_to_none():
    exc = ApiException(404, "not_found", "Not found")
    assert exc.error.field is None


async def test_validation_handler_maps_to_400_with_field():
    exc = RequestValidationError(
        errors=[
            {
                "type": "string_too_short",
                "loc": ("body", "username"),
                "msg": "String should have at least 3 characters",
                "input": "ab",
                "ctx": {"min_length": 3},
            }
        ]
    )

    request = Request(scope={"type": "http", "method": "POST", "path": "/test", "headers": []})
    response = await _validation_exception_handler(request=request, exc=exc)

    assert response.status_code == 400
    body = bytes(response.body).decode()
    assert '"code":"validation_error"' in body
    assert '"field":"username"' in body
