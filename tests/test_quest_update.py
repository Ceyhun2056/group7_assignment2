"""Verify the actual PUT endpoint, including ownership and validation."""

import pytest
from fastapi.testclient import TestClient

from app.main import app
from app.mock_data import create_mock_quests, quests


@pytest.fixture
def client():
    original = quests.copy()
    quests.clear()
    quests.update(create_mock_quests())
    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        quests.clear()
        quests.update(original)


@pytest.fixture
def body():
    return {
        "title": "Updated study plan", "description": "Review chapter two.",
        "deadline": "2026-12-01", "difficulty": "medium", "status": "completed",
    }


@pytest.mark.parametrize("token, quest_id, owner", [
    ("user-a-token", "quest_1", "user-a"),
    ("user-b-token", "quest_3", "user-b"),
    ("admin-token", "quest_1", "user-a"),
    ("admin-token", "quest_3", "user-b"),
])
def test_owner_or_admin_updates_quest(client, body, token, quest_id, owner):
    response = client.put(
        f"/api/v1/quests/{quest_id}", json=body,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    expected = {**body, "id": quest_id, "ownerId": owner}
    assert response.json() == {
        "success": True, "message": "Quest updated successfully.", "data": expected,
    }
    assert quests[quest_id].model_dump(mode="json") == expected


@pytest.mark.parametrize("token, quest_id, status, code", [
    (None, "quest_1", 401, "UNAUTHORIZED"),
    ("invalid-token", "quest_1", 401, "UNAUTHORIZED"),
    ("user-a-token", "quest_3", 403, "FORBIDDEN"),
    ("user-b-token", "quest_1", 403, "FORBIDDEN"),
    ("user-a-token", "quest_999", 404, "NOT_FOUND"),
    ("admin-token", "quest_999", 404, "NOT_FOUND"),
])
def test_denied_updates_do_not_change_data(client, body, token, quest_id, status, code):
    before = {key: value.model_dump() for key, value in quests.items()}
    headers = {} if token is None else {"Authorization": f"Bearer {token}"}
    response = client.put(f"/api/v1/quests/{quest_id}", json=body, headers=headers)
    assert response.status_code == status
    assert response.json()["error"]["code"] == code
    assert {key: value.model_dump() for key, value in quests.items()} == before


@pytest.mark.parametrize("changes", [
    {"title": "ab"}, {"difficulty": "extreme"}, {"deadline": "invalid"},
    {"ownerId": "user-b"}, {"id": "quest_999"}, {"extra": True},
])
def test_invalid_update_does_not_change_quest(client, body, changes):
    before = quests["quest_1"].model_dump()
    response = client.put(
        "/api/v1/quests/quest_1", json={**body, **changes},
        headers={"Authorization": "Bearer user-a-token"},
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert response.json()["error"]["details"][0]["field"] == next(iter(changes))
    assert quests["quest_1"].model_dump() == before


def test_put_requires_all_required_fields(client):
    response = client.put(
        "/api/v1/quests/quest_1", json={"title": "Only a title"},
        headers={"Authorization": "Bearer user-a-token"},
    )
    assert response.status_code == 400


def test_omitted_status_resets_to_open(client, body):
    del body["status"]
    response = client.put(
        "/api/v1/quests/quest_4", json=body,
        headers={"Authorization": "Bearer user-b-token"},
    )
    assert response.status_code == 200
    assert response.json()["data"]["status"] == "open"
