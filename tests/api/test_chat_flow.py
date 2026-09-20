from fastapi.testclient import TestClient

from tests.helpers import auth_headers
from tests.helpers import register_and_activate as _register_and_activate


def _create_chat(client: TestClient, headers: dict, name: str = "My chat") -> dict:
    response = client.post("/v1/chat/", json={"name": name}, headers=headers)
    assert response.status_code == 200, response.text
    return response.json()


async def test_create_chat_success(client: TestClient, fake_mailer):
    tokens = _register_and_activate(client, fake_mailer)
    headers = auth_headers(tokens)

    chat = _create_chat(client, headers)
    assert chat["name"] == "My chat"
    assert chat["status"] == "ongoing"
    assert chat["uuid"]


async def test_create_chat_requires_auth(client: TestClient):
    response = client.post("/v1/chat/", json={"name": "My chat"})
    assert response.status_code == 401
    assert response.json()["code"] == "missing_token"


async def test_get_chat_assembles_messages_in_sequence(client: TestClient, fake_mailer):
    tokens = _register_and_activate(client, fake_mailer)
    headers = auth_headers(tokens)
    chat = _create_chat(client, headers)

    first = client.post(
        f"/v1/chat/{chat['uuid']}/message/",
        json={"text": "hello"},
        headers=headers,
    )
    assert first.status_code == 200, first.text
    second = client.post(
        f"/v1/chat/{chat['uuid']}/message/",
        json={"text": "hi there", "is_ai": True},
        headers=headers,
    )
    assert second.status_code == 200, second.text

    response = client.get(f"/v1/chat/{chat['uuid']}", headers=headers)
    assert response.status_code == 200, response.text
    body = response.json()
    assert [m["text"] for m in body["messages"]] == ["hello", "hi there"]
    assert [m["sequence"] for m in body["messages"]] == [1, 2]
    assert body["messages"][1]["is_ai"] is True


async def test_get_chat_not_found(client: TestClient, fake_mailer):
    tokens = _register_and_activate(client, fake_mailer)
    headers = auth_headers(tokens)

    response = client.get("/v1/chat/00000000-0000-0000-0000-000000000000", headers=headers)
    assert response.status_code == 404
    assert response.json()["code"] == "chat_not_found"


async def test_chat_not_visible_to_other_user(client: TestClient, fake_mailer):
    tokens = _register_and_activate(client, fake_mailer)
    chat = _create_chat(client, auth_headers(tokens))

    other_tokens = _register_and_activate(
        client, fake_mailer, email="other@example.com", username="otheruser"
    )
    other_headers = auth_headers(other_tokens)

    response = client.get(f"/v1/chat/{chat['uuid']}", headers=other_headers)
    assert response.status_code == 404
    assert response.json()["code"] == "chat_not_found"

    message = client.post(
        f"/v1/chat/{chat['uuid']}/message/",
        json={"text": "sneaky"},
        headers=other_headers,
    )
    assert message.status_code == 404


async def test_delete_chat(client: TestClient, fake_mailer):
    tokens = _register_and_activate(client, fake_mailer)
    headers = auth_headers(tokens)
    chat = _create_chat(client, headers)

    response = client.delete(f"/v1/chat/{chat['uuid']}", headers=headers)
    assert response.status_code == 204

    response = client.get(f"/v1/chat/{chat['uuid']}", headers=headers)
    assert response.status_code == 404


async def test_delete_message(client: TestClient, fake_mailer):
    tokens = _register_and_activate(client, fake_mailer)
    headers = auth_headers(tokens)
    chat = _create_chat(client, headers)

    message = client.post(
        f"/v1/chat/{chat['uuid']}/message/", json={"text": "hello"}, headers=headers
    ).json()

    response = client.delete(f"/v1/chat/{chat['uuid']}/message/{message['uuid']}", headers=headers)
    assert response.status_code == 204

    response = client.get(f"/v1/chat/{chat['uuid']}/message/{message['uuid']}", headers=headers)
    assert response.status_code == 404
    assert response.json()["code"] == "message_not_found"


async def test_active_chat_roundtrip(client: TestClient, fake_mailer):
    tokens = _register_and_activate(client, fake_mailer)
    headers = auth_headers(tokens)
    chat = _create_chat(client, headers)

    missing = client.get("/v1/chat/active", headers=headers)
    assert missing.status_code == 404
    assert missing.json()["code"] == "no_active_chat"

    activate = client.put("/v1/chat/active", json={"uuid": chat["uuid"]}, headers=headers)
    assert activate.status_code == 204

    response = client.get("/v1/chat/active", headers=headers)
    assert response.status_code == 200
    assert response.json()["uuid"] == chat["uuid"]


async def test_activate_chat_not_owned_fails(client: TestClient, fake_mailer):
    tokens = _register_and_activate(client, fake_mailer)
    chat = _create_chat(client, auth_headers(tokens))

    other_tokens = _register_and_activate(
        client, fake_mailer, email="other@example.com", username="otheruser"
    )
    response = client.put(
        "/v1/chat/active",
        json={"uuid": chat["uuid"]},
        headers=auth_headers(other_tokens),
    )
    assert response.status_code == 404
    assert response.json()["code"] == "chat_not_found"
