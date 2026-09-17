from fastapi.testclient import TestClient

REGISTER_PAYLOAD = {
    "email": "test@example.com",
    "username": "testuser",
    "first_name": "Test",
    "last_name": "User",
    "password": "password123",
}


def register(client: TestClient, **overrides) -> dict:
    payload = {**REGISTER_PAYLOAD, **overrides}
    response = client.post("/v1/auth/register", json=payload)
    assert response.status_code == 200, response.text
    return response.json()


def activate(client: TestClient, code: str) -> dict:
    response = client.post("/v1/auth/register/activate", json={"code": code})
    assert response.status_code == 200, response.text
    return response.json()


def register_and_activate(client: TestClient, fake_mailer, **overrides) -> dict:
    register(client, **overrides)
    _, code = fake_mailer.sent[-1]
    return activate(client, code)


def auth_headers(tokens: dict) -> dict:
    return {"Authorization": f"Bearer {tokens['access_token']}"}
