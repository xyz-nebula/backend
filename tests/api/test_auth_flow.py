import pyotp
from fastapi.testclient import TestClient

from app.database.models import User, UserStatus

REGISTER_PAYLOAD = {
    "email": "test@example.com",
    "username": "testuser",
    "first_name": "Test",
    "last_name": "User",
    "password": "password123",
}


def _register(client: TestClient, **overrides) -> dict:
    payload = {**REGISTER_PAYLOAD, **overrides}
    response = client.post("/v1/auth/user/register", json=payload)
    assert response.status_code == 200, response.text
    return response.json()


def _activate(client: TestClient, code: str) -> dict:
    response = client.post("/v1/auth/user/register/activate", json={"code": code})
    assert response.status_code == 200, response.text
    return response.json()


def _register_and_activate(client, fake_mailer, **overrides) -> dict:
    _register(client, **overrides)
    _, code = fake_mailer.sent[-1]
    return _activate(client, code)


async def test_register_success(client: TestClient, fake_mailer):
    body = _register(client)
    assert body["status"] == "pending_activation"
    assert len(fake_mailer.sent) == 1
    email, code = fake_mailer.sent[0]
    assert email == REGISTER_PAYLOAD["email"]
    assert code


async def test_register_duplicate_email_conflicts(client: TestClient, fake_mailer):
    _register(client)
    response = client.post(
        "/v1/auth/user/register",
        json={**REGISTER_PAYLOAD, "username": "otheruser"},
    )
    assert response.status_code == 409
    assert response.json()["code"] == "email_taken"


async def test_register_duplicate_username_conflicts(client: TestClient, fake_mailer):
    _register(client)
    response = client.post(
        "/v1/auth/user/register",
        json={**REGISTER_PAYLOAD, "email": "other@example.com"},
    )
    assert response.status_code == 409
    assert response.json()["code"] == "username_taken"


async def test_register_validation_error(client: TestClient):
    response = client.post(
        "/v1/auth/user/register",
        json={**REGISTER_PAYLOAD, "username": "ab"},
    )
    assert response.status_code == 400
    assert response.json()["code"] == "validation_error"
    assert response.json()["field"] == "username"


async def test_activate_success(client: TestClient, fake_mailer):
    _register(client)
    _, code = fake_mailer.sent[0]
    tokens = _activate(client, code)
    assert tokens["access_token"]
    assert tokens["refresh_token"]

    user = await User.get(email=REGISTER_PAYLOAD["email"])
    assert user.status == UserStatus.ACTIVE


async def test_activate_bogus_code_returns_404(client: TestClient):
    response = client.post(
        "/v1/auth/user/register/activate",
        json={"code": "00000000-0000-0000-0000-000000000000"},
    )
    assert response.status_code == 404
    assert response.json()["code"] == "activation_code_not_found"


async def test_activate_code_cannot_be_reused(client: TestClient, fake_mailer):
    _register(client)
    _, code = fake_mailer.sent[0]
    _activate(client, code)

    response = client.post("/v1/auth/user/register/activate", json={"code": code})
    assert response.status_code == 404


async def test_login_before_activation_forbidden(client: TestClient, fake_mailer):
    _register(client)
    response = client.post(
        "/v1/auth/user/login",
        json={"email": REGISTER_PAYLOAD["email"], "password": REGISTER_PAYLOAD["password"]},
    )
    assert response.status_code == 403
    assert response.json()["code"] == "account_not_activated"


async def test_login_suspended_user_forbidden(client: TestClient, fake_mailer):
    _register_and_activate(client, fake_mailer)
    user = await User.get(email=REGISTER_PAYLOAD["email"])
    user.status = UserStatus.SUSPENDED
    await user.save(update_fields=["status"])

    response = client.post(
        "/v1/auth/user/login",
        json={"email": REGISTER_PAYLOAD["email"], "password": REGISTER_PAYLOAD["password"]},
    )
    assert response.status_code == 403
    assert response.json()["code"] == "account_suspended"


async def test_login_wrong_password(client: TestClient, fake_mailer):
    _register_and_activate(client, fake_mailer)
    response = client.post(
        "/v1/auth/user/login",
        json={"email": REGISTER_PAYLOAD["email"], "password": "wrong-password"},
    )
    assert response.status_code == 401
    assert response.json()["code"] == "invalid_credentials"


async def test_login_success(client: TestClient, fake_mailer):
    _register_and_activate(client, fake_mailer)
    response = client.post(
        "/v1/auth/user/login",
        json={"email": REGISTER_PAYLOAD["email"], "password": REGISTER_PAYLOAD["password"]},
    )
    assert response.status_code == 200
    assert response.json()["access_token"]


async def test_login_mfa_required_when_enabled(client: TestClient, fake_mailer):
    _register_and_activate(client, fake_mailer)
    user = await User.get(email=REGISTER_PAYLOAD["email"])
    secret = pyotp.random_base32()
    user.mfa_enabled = True
    user.mfa_secret = secret
    await user.save(update_fields=["mfa_enabled", "mfa_secret"])

    response = client.post(
        "/v1/auth/user/login",
        json={"email": REGISTER_PAYLOAD["email"], "password": REGISTER_PAYLOAD["password"]},
    )
    assert response.status_code == 401
    assert response.json()["code"] == "mfa_required"

    wrong = client.post(
        "/v1/auth/user/login",
        json={
            "email": REGISTER_PAYLOAD["email"],
            "password": REGISTER_PAYLOAD["password"],
            "totp_token": "000000",
        },
    )
    assert wrong.status_code == 401
    assert wrong.json()["code"] == "invalid_credentials"

    correct = client.post(
        "/v1/auth/user/login",
        json={
            "email": REGISTER_PAYLOAD["email"],
            "password": REGISTER_PAYLOAD["password"],
            "totp_token": pyotp.TOTP(secret).now(),
        },
    )
    assert correct.status_code == 200


async def test_refresh_rotates_token(client: TestClient, fake_mailer):
    tokens = _register_and_activate(client, fake_mailer)
    old_refresh = tokens["refresh_token"]

    response = client.post("/v1/auth/token/refresh", json={"refresh_token": old_refresh})
    assert response.status_code == 200
    new_tokens = response.json()
    assert new_tokens["refresh_token"] != old_refresh

    reuse = client.post("/v1/auth/token/refresh", json={"refresh_token": old_refresh})
    assert reuse.status_code == 401
    assert reuse.json()["code"] == "invalid_token"


async def test_logout_requires_bearer_token(client: TestClient, fake_mailer):
    tokens = _register_and_activate(client, fake_mailer)
    response = client.post(
        "/v1/auth/user/logout", json={"refresh_token": tokens["refresh_token"]}
    )
    assert response.status_code == 401


async def test_logout_invalidates_refresh_token(client: TestClient, fake_mailer):
    tokens = _register_and_activate(client, fake_mailer)

    response = client.post(
        "/v1/auth/user/logout",
        json={"refresh_token": tokens["refresh_token"]},
        headers={"Authorization": f"Bearer {tokens['access_token']}"},
    )
    assert response.status_code == 204

    refresh_after_logout = client.post(
        "/v1/auth/token/refresh", json={"refresh_token": tokens["refresh_token"]}
    )
    assert refresh_after_logout.status_code == 401
