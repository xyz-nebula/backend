import pyotp
from fastapi.testclient import TestClient

from app.database.models import User
from tests.helpers import REGISTER_PAYLOAD
from tests.helpers import auth_headers as _auth_headers
from tests.helpers import register_and_activate as _register_and_activate


async def test_enroll_returns_secret_and_otpauth_url(client: TestClient, fake_mailer):
    tokens = _register_and_activate(client, fake_mailer)
    response = client.post("/v1/auth/totp/enroll", headers=_auth_headers(tokens))
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["secret"]
    assert body["otpauth_url"].startswith("otpauth://totp/")

    user = await User.get(email=REGISTER_PAYLOAD["email"])
    assert user.mfa_secret == body["secret"]
    assert user.mfa_enabled is False


async def test_enroll_without_bearer_token(client: TestClient, fake_mailer):
    response = client.post("/v1/auth/totp/enroll")
    assert response.status_code == 401
    assert response.json()["code"] == "missing_token"


async def test_enroll_with_garbage_token(client: TestClient, fake_mailer):
    response = client.post(
        "/v1/auth/totp/enroll", headers={"Authorization": "Bearer not-a-real-token"}
    )
    assert response.status_code == 401
    assert response.json()["code"] == "invalid_token"


async def test_enroll_fails_when_already_enabled(client: TestClient, fake_mailer):
    tokens = _register_and_activate(client, fake_mailer)
    secret = _enroll(client, tokens)
    _confirm(client, tokens, secret)

    response = client.post("/v1/auth/totp/enroll", headers=_auth_headers(tokens))
    assert response.status_code == 409
    assert response.json()["code"] == "mfa_already_enabled"


async def test_confirm_enables_mfa(client: TestClient, fake_mailer):
    tokens = _register_and_activate(client, fake_mailer)
    secret = _enroll(client, tokens)

    response = client.post(
        "/v1/auth/totp/confirm",
        json={"totp_token": pyotp.TOTP(secret).now()},
        headers=_auth_headers(tokens),
    )
    assert response.status_code == 204

    user = await User.get(email=REGISTER_PAYLOAD["email"])
    assert user.mfa_enabled is True


async def test_confirm_without_enrolling_first(client: TestClient, fake_mailer):
    tokens = _register_and_activate(client, fake_mailer)
    response = client.post(
        "/v1/auth/totp/confirm",
        json={"totp_token": "000000"},
        headers=_auth_headers(tokens),
    )
    assert response.status_code == 400
    assert response.json()["code"] == "totp_not_enrolled"


async def test_confirm_with_wrong_code(client: TestClient, fake_mailer):
    tokens = _register_and_activate(client, fake_mailer)
    _enroll(client, tokens)

    response = client.post(
        "/v1/auth/totp/confirm",
        json={"totp_token": "000000"},
        headers=_auth_headers(tokens),
    )
    assert response.status_code == 401
    assert response.json()["code"] == "invalid_totp_token"


async def test_disable_turns_off_mfa(client: TestClient, fake_mailer):
    tokens = _register_and_activate(client, fake_mailer)
    secret = _enroll(client, tokens)
    _confirm(client, tokens, secret)

    response = client.request(
        "DELETE",
        "/v1/auth/totp",
        json={"password": REGISTER_PAYLOAD["password"]},
        headers=_auth_headers(tokens),
    )
    assert response.status_code == 204

    user = await User.get(email=REGISTER_PAYLOAD["email"])
    assert user.mfa_enabled is False
    assert user.mfa_secret is None


async def test_disable_when_not_enabled(client: TestClient, fake_mailer):
    tokens = _register_and_activate(client, fake_mailer)
    response = client.request(
        "DELETE",
        "/v1/auth/totp",
        json={"password": REGISTER_PAYLOAD["password"]},
        headers=_auth_headers(tokens),
    )
    assert response.status_code == 409
    assert response.json()["code"] == "mfa_not_enabled"


async def test_disable_with_wrong_password(client: TestClient, fake_mailer):
    tokens = _register_and_activate(client, fake_mailer)
    secret = _enroll(client, tokens)
    _confirm(client, tokens, secret)

    response = client.request(
        "DELETE",
        "/v1/auth/totp",
        json={"password": "wrong-password"},
        headers=_auth_headers(tokens),
    )
    assert response.status_code == 401
    assert response.json()["code"] == "invalid_credentials"


async def test_full_enroll_confirm_login_flow(client: TestClient, fake_mailer):
    tokens = _register_and_activate(client, fake_mailer)
    secret = _enroll(client, tokens)
    _confirm(client, tokens, secret)

    without_totp = client.post(
        "/v1/auth/login",
        json={"email": REGISTER_PAYLOAD["email"], "password": REGISTER_PAYLOAD["password"]},
    )
    assert without_totp.status_code == 401
    assert without_totp.json()["code"] == "mfa_required"

    with_totp = client.post(
        "/v1/auth/login",
        json={
            "email": REGISTER_PAYLOAD["email"],
            "password": REGISTER_PAYLOAD["password"],
            "totp_token": pyotp.TOTP(secret).now(),
        },
    )
    assert with_totp.status_code == 200


def _enroll(client: TestClient, tokens: dict) -> str:
    response = client.post("/v1/auth/totp/enroll", headers=_auth_headers(tokens))
    assert response.status_code == 200, response.text
    return response.json()["secret"]


def _confirm(client: TestClient, tokens: dict, secret: str) -> None:
    response = client.post(
        "/v1/auth/totp/confirm",
        json={"totp_token": pyotp.TOTP(secret).now()},
        headers=_auth_headers(tokens),
    )
    assert response.status_code == 204, response.text
