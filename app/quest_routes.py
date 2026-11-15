"""Quest listing and retrieval endpoints."""

from fastapi import APIRouter, Depends, Query

from app.auth import User, can_access_quest, get_accessible_quest, get_current_user
from app.mock_data import quests
from app.responses import success_response

router = APIRouter(prefix="/api/v1/quests", tags=["Quests"])


@router.get(
    "",
    responses={
        400: {"description": "Invalid pagination parameters."},
        401: {"description": "Missing or invalid Bearer token."},
    },
)
def list_quests(
    page: int = Query(default=1, ge=1),
    perPage: int = Query(default=10, ge=1, le=100),
    user: User = Depends(get_current_user),
) -> dict:
    """Filter by access before counting or paginating the results."""
    visible = [quest for quest in quests.values() if can_access_quest(user, quest)]
    start = (page - 1) * perPage
    data = [quest.model_dump(mode="json") for quest in visible[start:start + perPage]]
    return success_response(
        "Quests retrieved successfully.", data,
        meta={"total": len(visible), "page": page, "perPage": perPage},
    )


@router.get(
    "/{quest_id}",
    responses={
        401: {"description": "Missing or invalid Bearer token."},
        403: {"description": "The quest belongs to another user."},
        404: {"description": "The quest does not exist."},
    },
)
def get_quest(quest_id: str, user: User = Depends(get_current_user)) -> dict:
    quest = get_accessible_quest(quest_id, user)
    return success_response("Quest retrieved successfully.", quest.model_dump(mode="json"))
