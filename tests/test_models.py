"""Small checks for quest validation and the required initial mock data."""

import pytest
from pydantic import ValidationError

from app.mock_data import create_mock_quests
from app.models import QuestInput


@pytest.fixture
def quest_body():
    return {
        "title": "Study REST", "description": "Review the API notes.",
        "deadline": "2026-11-20", "difficulty": "easy",
    }


def test_valid_quest_trims_text_and_defaults_to_open(quest_body):
    quest_body["title"] = "  Study REST  "
    quest = QuestInput(**quest_body)
    assert quest.model_dump(mode="json") == {**quest_body, "title": "Study REST", "status": "open"}


@pytest.mark.parametrize("field", ["title", "description", "deadline", "difficulty"])
def test_required_fields(quest_body, field):
    del quest_body[field]
    with pytest.raises(ValidationError) as error:
        QuestInput(**quest_body)
    assert error.value.errors()[0]["loc"] == (field,)


@pytest.mark.parametrize("field, value", [
    ("title", "ab"), ("title", " " * 5), ("title", "a" * 121), ("title", 123),
    ("description", ""), ("description", " " * 5),
    ("description", "a" * 2001), ("description", 123),
    ("deadline", "2026-02-30"), ("deadline", "not-a-date"), ("deadline", 0),
    ("deadline", "2026-11-20T00:00:00"),
    ("difficulty", "extreme"), ("status", "invalid"),
    ("ownerId", "user-b"), ("id", "quest_99"), ("unknown", "value"),
])
def test_invalid_values_and_unknown_fields(quest_body, field, value):
    quest_body[field] = value
    with pytest.raises(ValidationError) as error:
        QuestInput(**quest_body)
    assert error.value.errors()[0]["loc"] == (field,)


def test_completed_quest_can_have_a_past_deadline(quest_body):
    quest_body.update(status="completed", difficulty="hard", deadline="2020-01-01")
    assert QuestInput(**quest_body).status == "completed"


def test_mock_data_has_two_quests_per_user_and_a_missing_demo_id():
    quests = create_mock_quests()
    assert sum(quest.ownerId == "user-a" for quest in quests.values()) == 2
    assert sum(quest.ownerId == "user-b" for quest in quests.values()) == 2
    assert all(key == quest.id for key, quest in quests.items())
    assert "quest_999" not in quests


def test_resetting_mock_data_returns_independent_quests():
    changed = create_mock_quests()
    changed["quest_1"].title = "Changed title"
    del changed["quest_2"]
    fresh = create_mock_quests()
    assert fresh["quest_1"].title == "Review REST API notes"
    assert "quest_2" in fresh
