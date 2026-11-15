"""Check authentication and access helpers before quest routes are added."""

import pytest
from fastapi import Depends, FastAPI
from fastapi.testclient import TestClient

from app.auth import MOCK_USERS, User, can_access_quest, get_accessible_quest, get_current_user
from app.main import app
from app.mock_data import quests
from app.responses import success_response


@pytest.fixture
def client():
    # Keep the test endpoint separate from the actual application.
    test_app = FastAPI(exception_handlers=app.exception_handlers)

    @test_app.get("/test/quests/{quest_id}")
    def read_quest(quest_id: str, user: User = Depends(get_current_user)):
        quest = get_accessible_quest(quest_id, user)
        return success_response("Quest retrieved.", quest.model_dump(mode="json"))

    with TestClient(test_app) as test_client:
        yield test_client


@pytest.mark.parametrize("authorization", [
    None, "", "Bearer", "Bearer invalid-token", "Basic user-a-token",
    "Bearer user-a-token extra", "Bearer USER-A-TOKEN",
])
def test_missing_invalid_and_malformed_tokens_return_401(client, authorization):
    headers = {} if authorization is None else {"Authorization": authorization}
    response = client.get("/test/quests/quest_1", headers=headers)
    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"
    assert response.json() == {
        "success": False,
        "error": {"code": "UNAUTHORIZED", "message": "A valid Bearer token is required."},
    }


@pytest.mark.parametrize("token, quest_id", [
    ("user-a-token", "quest_1"), ("user-a-token", "quest_2"),
    ("user-b-token", "quest_3"), ("user-b-token", "quest_4"),
    ("admin-token", "quest_1"), ("admin-token", "quest_2"),
    ("admin-token", "quest_3"), ("admin-token", "quest_4"),
])
def test_owners_and_administrator_can_access_quests(client, token, quest_id):
    response = client.get(
        f"/test/quests/{quest_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 200
    assert response.json()["data"]["id"] == quest_id


@pytest.mark.parametrize("token, quest_id", [
    ("user-a-token", "quest_3"), ("user-a-token", "quest_4"),
    ("user-b-token", "quest_1"), ("user-b-token", "quest_2"),
])
def test_users_cannot_access_each_others_quests(client, token, quest_id):
    response = client.get(
        f"/test/quests/{quest_id}", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 403
    assert response.json()["error"]["code"] == "FORBIDDEN"
    assert "data" not in response.json()


@pytest.mark.parametrize("token", list(MOCK_USERS))
def test_missing_quest_returns_404_for_each_role(client, token):
    response = client.get(
        "/test/quests/quest_999", headers={"Authorization": f"Bearer {token}"}
    )
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"


def test_authentication_runs_before_quest_lookup(client):
    assert client.get("/test/quests/quest_999").status_code == 401


@pytest.mark.parametrize("token, expected_ids", [
    ("user-a-token", {"quest_1", "quest_2"}),
    ("user-b-token", {"quest_3", "quest_4"}),
    ("admin-token", {"quest_1", "quest_2", "quest_3", "quest_4"}),
])
def test_access_filter_selects_only_allowed_quests(token, expected_ids):
    user = MOCK_USERS[token]
    visible_ids = {quest.id for quest in quests.values() if can_access_quest(user, quest)}
    assert visible_ids == expected_ids
