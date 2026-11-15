"""Quest fields shared by creation, replacement, and stored mock data."""

from datetime import date
import re
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class QuestInput(BaseModel):
    # Reject unknown fields, including client-supplied IDs and ownership.
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)

    title: str = Field(strict=True, min_length=3, max_length=120)
    description: str = Field(strict=True, min_length=1, max_length=2000)
    deadline: date
    difficulty: Literal["easy", "medium", "hard"]
    status: Literal["open", "completed"] = "open"

    @field_validator("deadline", mode="before")
    @classmethod
    def validate_deadline_type(cls, value):
        # Pydantic also accepts numeric timestamps; this API expects a date.
        if not isinstance(value, (str, date)):
            raise ValueError("Deadline must be a date in YYYY-MM-DD format.")
        if isinstance(value, str) and not re.fullmatch(r"\d{4}-\d{2}-\d{2}", value):
            raise ValueError("Deadline must be a date in YYYY-MM-DD format.")
        return value


class Quest(QuestInput):
    id: str = Field(strict=True, min_length=1)
    ownerId: str = Field(strict=True, min_length=1)
