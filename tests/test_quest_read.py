"""Verify the real GET endpoints and ownership-aware pagination."""

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


@pytest.mark.parametrize("token, expected_ids", [
    ("user-a-token", ["quest_1", "quest_2"]),
    ("user-b-token", ["quest_3", "quest_4"]),
    ("admin-token", ["quest_1", "quest_2", "quest_3", "quest_4"]),
])
def test_list_filters_data_and_total_by_user(client, token, expected_ids):
    response = client.get("/api/v1/quests", headers={"Authorization": f"Bearer {token}"})
    assert response.status_code == 200
    result = response.json()
    assert result["success"] is True
    assert [quest["id"] for quest in result["data"]] == expected_ids
    assert result["meta"] == {"total": len(expected_ids), "page": 1, "perPage": 10}


def test_pagination_is_applied_after_ownership_filter(client):
    response = client.get(
        "/api/v1/quests?page=2&perPage=1",
        headers={"Authorization": "Bearer user-b-token"},
    )
    assert response.status_code == 200
    assert [quest["id"] for quest in response.json()["data"]] == ["quest_4"]
    assert response.json()["meta"] == {"total": 2, "page": 2, "perPage": 1}


def test_page_beyond_results_returns_empty_list(client):
    response = client.get(
        "/api/v1/quests?page=5", headers={"Authorization": "Bearer user-a-token"}
    )
    assert response.status_code == 200
    assert response.json()["data"] == []
    assert response.json()["meta"]["total"] == 2


@pytest.mark.parametrize("query, field", [
    ("page=0", "page"), ("page=abc", "page"),
    ("perPage=0", "perPage"), ("perPage=101", "perPage"),
])
def test_invalid_pagination_returns_400(client, query, field):
    response = client.get(
        f"/api/v1/quests?{query}", headers={"Authorization": "Bearer user-a-token"}
    )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    assert response.json()["error"]["details"][0]["field"] == field


@pytest.mark.parametrize("path", ["/api/v1/quests", "/api/v1/quests/quest_1"])
@pytest.mark.parametrize("token", [None, "invalid-token"])
def test_get_endpoints_require_valid_authentication(client, path, token):
    headers = {} if token is None else {"Authorization": f"Bearer {token}"}
    response = client.get(path, headers=headers)
    assert response.status_code == 401
    assert response.json()["error"]["code"] == "UNAUTHORIZED"


@pytest.mark.parametrize("token, quest_id, expected_status", [
    ("user-a-token", "quest_1", 200), ("user-b-token", "quest_3", 200),
    ("admin-token", "quest_1", 200), ("admin-token", "quest_3", 200),
    ("user-a-token", "quest_3", 403), ("user-b-token", "quest_1", 403),
    ("user-a-token", "quest_999", 404), ("admin-token", "quest_999", 404),
])
def test_single_quest_access(client, token, quest_id, expected_status):
    response = client.get(
        f"/api/v1/quests/{quest_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == expected_status
    if expected_status == 200:
        assert response.json()["data"] == quests[quest_id].model_dump(mode="json")
    else:
        code = "FORBIDDEN" if expected_status == 403 else "NOT_FOUND"
        assert response.json()["error"]["code"] == code


def test_get_requests_do_not_modify_quests(client):
    before = {key: quest.model_dump() for key, quest in quests.items()}
    headers = {"Authorization": "Bearer admin-token"}
    client.get("/api/v1/quests", headers=headers)
    client.get("/api/v1/quests/quest_1", headers=headers)
    assert {key: quest.model_dump() for key, quest in quests.items()} == before
