"""Update and delete existing quests after checking access."""

from fastapi import APIRouter, Depends

from app.auth import User, get_accessible_quest, get_current_user
from app.mock_data import quests
from app.models import Quest, QuestInput
from app.responses import success_response

router = APIRouter(
    prefix="/api/v1/quests",
    tags=["Quests"],
    # Suppress FastAPI's automatic 422 entry: validation errors use HTTP 400.
    responses={"default": {"description": "Error with success=false and an error code and message."}},
)


@router.put(
    "/{quest_id}",
    responses={
        400: {"description": "Invalid or missing quest fields."},
        401: {"description": "Missing or invalid Bearer token."},
        403: {"description": "The quest belongs to another user."},
        404: {"description": "The quest does not exist."},
    },
)
def update_quest(
    quest_id: str,
    body: QuestInput,
    user: User = Depends(get_current_user),
) -> dict:
    """Replace a quest after checking ownership or administrator access."""
    existing = get_accessible_quest(quest_id, user)
    updated = Quest(
        **body.model_dump(), id=existing.id, ownerId=existing.ownerId
    )
    quests[quest_id] = updated
    return success_response("Quest updated successfully.", updated.model_dump(mode="json"))


@router.delete(
    "/{quest_id}",
    responses={
        401: {"description": "Missing or invalid Bearer token."},
        403: {"description": "The quest belongs to another user."},
        404: {"description": "The quest does not exist."},
    },
)
def delete_quest(quest_id: str, user: User = Depends(get_current_user)) -> dict:
    """Remove a quest only after its owner or an administrator is authorized."""
    quest = get_accessible_quest(quest_id, user)
    del quests[quest.id]
    return success_response("Quest deleted successfully.")
