"""Exercise quest creation through the public API."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.mock_data import quests

QUESTS_URL = "/api/v1/quests"
VALID_QUEST = {
    "title": "Prepare API demo",
    "description": "Practice the quest endpoints.",
    "deadline": "2026-11-25",
    "difficulty": "medium",
}


def bearer(token):
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def client():
    original = quests.copy()
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        quests.clear()
        quests.update(original)


def test_created_quest_is_visible_to_owner_and_admin(client):
    owner = bearer("user-a-token")
    response = client.post(QUESTS_URL, json=VALID_QUEST, headers=owner)
    assert response.status_code == 201
    result = response.json()
    assert result["success"] is True
    quest = result["data"]
    assert quest == {**VALID_QUEST, "id": quest["id"], "ownerId": "user-a", "status": "open"}
    assert quest in client.get(QUESTS_URL, headers=owner).json()["data"]

    detail_url = f"{QUESTS_URL}/{quest['id']}"
    assert client.get(detail_url, headers=owner).json()["data"] == quest
    assert client.get(detail_url, headers=bearer("admin-token")).json()["data"] == quest
    other_user = bearer("user-b-token")
    assert client.get(detail_url, headers=other_user).status_code == 403
    assert quest not in client.get(QUESTS_URL, headers=other_user).json()["data"]


def test_each_creation_gets_a_distinct_id(client):
    headers = bearer("user-b-token")
    existing_ids = set(quests)
    first = client.post(QUESTS_URL, json=VALID_QUEST, headers=headers)
    second = client.post(QUESTS_URL, json=VALID_QUEST, headers=headers)
    assert first.status_code == second.status_code == 201
    first_quest, second_quest = first.json()["data"], second.json()["data"]
    assert first_quest["ownerId"] == second_quest["ownerId"] == "user-b"
    assert len({first_quest["id"], second_quest["id"]} - existing_ids) == 2


@pytest.mark.parametrize("headers", [{}, {"Authorization": "Bearer invalid-token"}])
def test_creation_requires_valid_authentication(client, headers):
    before = quests.copy()
    response = client.post(QUESTS_URL, json=VALID_QUEST, headers=headers)
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"
    assert quests == before


@pytest.mark.parametrize(
    "body, field",
    [
        ({}, "title"),
        ({**VALID_QUEST, "difficulty": "extreme"}, "difficulty"),
        ({**VALID_QUEST, "ownerId": "user-b"}, "ownerId"),
    ],
)
def test_invalid_body_creates_no_quest(client, body, field):
    before = quests.copy()
    response = client.post(QUESTS_URL, json=body, headers=bearer("user-a-token"))
    assert response.status_code == 400
    error = response.json()["error"]
    assert error["code"] == "VALIDATION_ERROR"
    assert field in {detail["field"] for detail in error["details"]}
    assert quests == before
