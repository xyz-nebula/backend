from uuid import uuid4

from fastapi.testclient import TestClient

from tests.helpers import auth_headers, make_admin, register_and_activate

CASE_PAYLOAD = {
    "name": "Admin case",
    "description": "Created by an admin",
    "category": "network",
    "difficulty": "hard",
    "time_limit": 45,
    "system_prompt": "You are the suspect",
    "goal": "Get a confession",
    "synopsis": "A heist gone wrong",
    "first_role": "Detective",
    "second_role": "Suspect",
    "first_role_preparations": "Review the evidence",
    "second_role_preparations": "Prepare an alibi",
}


def _admin_headers(client: TestClient, fake_mailer) -> dict:
    tokens = register_and_activate(client, fake_mailer)
    make_admin(client, tokens)
    return auth_headers(tokens)


async def test_non_admin_cannot_manage_cases(client: TestClient, fake_mailer):
    headers = auth_headers(register_and_activate(client, fake_mailer))

    assert client.get("/v1/cases/", headers=headers).status_code == 403
    assert client.post("/v1/cases/", json=CASE_PAYLOAD, headers=headers).status_code == 403
    response = client.patch(f"/v1/cases/{uuid4()}", json={"name": "x"}, headers=headers)
    assert response.status_code == 403


async def test_case_routes_require_auth(client: TestClient):
    assert client.get("/v1/cases/").status_code == 401
    assert client.post("/v1/cases/", json=CASE_PAYLOAD).status_code == 401


async def test_admin_creates_and_lists_case(client: TestClient, fake_mailer):
    headers = _admin_headers(client, fake_mailer)

    created = client.post("/v1/cases/", json=CASE_PAYLOAD, headers=headers)
    assert created.status_code == 200, created.text
    assert created.json()["name"] == "Admin case"
    assert created.json()["difficulty"] == "hard"
    for field in ("system_prompt", "goal", "synopsis", "first_role", "second_role"):
        assert created.json()[field] == CASE_PAYLOAD[field]

    listed = client.get("/v1/cases/", headers=headers)
    assert listed.status_code == 200, listed.text
    assert [c["uuid"] for c in listed.json()] == [created.json()["uuid"]]


async def test_admin_edits_case(client: TestClient, fake_mailer):
    headers = _admin_headers(client, fake_mailer)
    case = client.post("/v1/cases/", json=CASE_PAYLOAD, headers=headers).json()

    response = client.patch(
        f"/v1/cases/{case['uuid']}", json={"name": "Renamed", "time_limit": 10}, headers=headers
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["name"] == "Renamed"
    assert body["time_limit"] == 10
    assert body["description"] == CASE_PAYLOAD["description"]

    response = client.patch(
        f"/v1/cases/{case['uuid']}",
        json={"goal": "New goal", "system_prompt": "New prompt", "second_role": "Witness"},
        headers=headers,
    )
    assert response.status_code == 200, response.text
    body = response.json()
    assert body["goal"] == "New goal"
    assert body["system_prompt"] == "New prompt"
    assert body["second_role"] == "Witness"
    assert body["synopsis"] == CASE_PAYLOAD["synopsis"]
    assert body["name"] == "Renamed"


async def test_admin_edit_unknown_case(client: TestClient, fake_mailer):
    headers = _admin_headers(client, fake_mailer)

    response = client.patch(f"/v1/cases/{uuid4()}", json={"name": "x"}, headers=headers)
    assert response.status_code == 404
    assert response.json()["code"] == "case_not_found"


async def test_create_case_requires_new_fields(client: TestClient, fake_mailer):
    headers = _admin_headers(client, fake_mailer)

    for field in ("system_prompt", "goal", "synopsis", "first_role", "second_role"):
        payload = {k: v for k, v in CASE_PAYLOAD.items() if k != field}
        response = client.post("/v1/cases/", json=payload, headers=headers)
        assert response.status_code == 400, (field, response.text)
        assert response.json()["code"] == "validation_error"
