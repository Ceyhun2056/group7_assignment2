"""Check deletion, access control, and the update/delete sequence."""

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


@pytest.mark.parametrize("token, quest_id", [
    ("user-a-token", "quest_1"), ("user-b-token", "quest_3"),
    ("admin-token", "quest_1"), ("admin-token", "quest_3"),
])
def test_owner_or_admin_can_delete_quest(client, token, quest_id):
    before = set(quests)
    response = client.delete(
        f"/api/v1/quests/{quest_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json() == {
        "success": True, "message": "Quest deleted successfully.", "data": None,
    }
    assert set(quests) == before - {quest_id}


@pytest.mark.parametrize("token, quest_id, status, code", [
    (None, "quest_1", 401, "UNAUTHORIZED"),
    ("invalid-token", "quest_1", 401, "UNAUTHORIZED"),
    ("user-a-token", "quest_3", 403, "FORBIDDEN"),
    ("user-b-token", "quest_1", 403, "FORBIDDEN"),
    ("user-a-token", "quest_999", 404, "NOT_FOUND"),
    ("user-b-token", "quest_999", 404, "NOT_FOUND"),
    ("admin-token", "quest_999", 404, "NOT_FOUND"),
])
def test_failed_deletion_preserves_all_data(client, token, quest_id, status, code):
    before = {key: quest.model_dump() for key, quest in quests.items()}
    headers = {} if token is None else {"Authorization": f"Bearer {token}"}
    response = client.delete(f"/api/v1/quests/{quest_id}", headers=headers)
    assert response.status_code == status
    assert response.json()["error"]["code"] == code
    assert "details" not in response.json()["error"]
    assert {key: quest.model_dump() for key, quest in quests.items()} == before


def test_repeated_deletion_returns_404(client):
    headers = {"Authorization": "Bearer user-a-token"}
    assert client.delete("/api/v1/quests/quest_1", headers=headers).status_code == 200
    response = client.delete("/api/v1/quests/quest_1", headers=headers)
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
    assert len(quests) == 3


def test_update_then_delete_and_reject_further_update(client):
    headers = {"Authorization": "Bearer user-a-token"}
    body = {
        "title": "Updated quest", "description": "Prepare the demo.",
        "deadline": "2026-12-01", "difficulty": "easy",
    }
    assert client.put("/api/v1/quests/quest_1", json=body, headers=headers).status_code == 200
    assert client.delete("/api/v1/quests/quest_1", headers=headers).status_code == 200
    response = client.put("/api/v1/quests/quest_1", json=body, headers=headers)
    assert response.status_code == 404
    assert "quest_1" not in quests
