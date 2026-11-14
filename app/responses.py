"""Shared JSON envelopes for the LifeQuest API."""

from typing import Any


def success_response(
    message: str, data: Any = None, *, meta: dict | None = None
) -> dict:
    """Build a success body; the endpoint sets the appropriate 2xx status."""
    body = {"success": True, "message": message, "data": data}
    if meta is not None:
        body["meta"] = meta
    return body


def error_response(
    code: str, message: str, *, details: list[dict[str, str]] | None = None
) -> dict:
    """Build an error body, including field details only for validation."""
    error = {"code": code, "message": message}
    if code == "VALIDATION_ERROR" and details is not None:
        error["details"] = details
    return {"success": False, "error": error}
