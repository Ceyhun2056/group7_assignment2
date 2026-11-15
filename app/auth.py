"""Predefined mock users and shared quest access checks."""

from dataclasses import dataclass
from typing import Literal

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from app.mock_data import quests
from app.models import Quest


@dataclass(frozen=True)
class User:
    id: str
    role: Literal["user", "admin"]


MOCK_USERS = {
    "user-a-token": User(id="user-a", role="user"),
    "user-b-token": User(id="user-b", role="user"),
    "admin-token": User(id="admin", role="admin"),
}

# Handle failed authentication ourselves so every failure uses HTTP 401.
bearer = HTTPBearer(auto_error=False)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer),
) -> User:
    user = MOCK_USERS.get(credentials.credentials) if credentials else None
    if user is None:
        raise HTTPException(
            status_code=401,
            detail="A valid Bearer token is required.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def can_access_quest(user: User, quest: Quest) -> bool:
    """Also used to filter collection results before pagination."""
    return user.role == "admin" or quest.ownerId == user.id


def get_accessible_quest(quest_id: str, user: User) -> Quest:
    """Find a quest and check access before reading, updating, or deleting it."""
    quest = quests.get(quest_id)
    if quest is None:
        raise HTTPException(status_code=404, detail="Quest not found.")
    if not can_access_quest(user, quest):
        raise HTTPException(status_code=403, detail="You cannot access another user's quest.")
    return quest
