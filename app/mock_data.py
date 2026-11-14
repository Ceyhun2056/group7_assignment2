"""In-memory quest storage; all changes are lost when the server restarts."""

from app.models import Quest


def create_mock_quests() -> dict[str, Quest]:
    """Return fresh starting data so tests can also reset the store."""
    initial_quests = [
        Quest(
            id="quest_1", ownerId="user-a", title="Review REST API notes",
            description="Revise resources, HTTP methods, and status codes.",
            deadline="2026-11-20", difficulty="easy",
        ),
        Quest(
            id="quest_2", ownerId="user-a", title="Prepare project presentation",
            description="Outline the LifeQuest project presentation.",
            deadline="2026-11-22", difficulty="medium",
        ),
        Quest(
            id="quest_3", ownerId="user-b", title="Practice data structures",
            description="Solve the assigned tree and heap exercises.",
            deadline="2026-11-21", difficulty="hard",
        ),
        Quest(
            id="quest_4", ownerId="user-b", title="Read the project proposal",
            description="Review the LifeQuest features and target users.",
            deadline="2026-11-14", difficulty="easy", status="completed",
        ),
    ]
    return {quest.id: quest for quest in initial_quests}


quests = create_mock_quests()
