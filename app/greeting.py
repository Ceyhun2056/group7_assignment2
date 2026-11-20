"""Public HTML introduction and live API endpoint list."""

from html import escape
from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse

router = APIRouter()
PAGE = Path(__file__).with_name("greeting.html").read_text(encoding="utf-8")
DESCRIPTIONS = {
    ("GET", "/api/v1/greeting"): "View this project and team introduction.",
    ("GET", "/api/v1/quests"): "List your quests with pagination; administrators see all quests.",
    ("GET", "/api/v1/quests/{quest_id}"): "View a quest you are allowed to access.",
    ("POST", "/api/v1/quests"): "Create a quest owned by the authenticated user.",
    ("PUT", "/api/v1/quests/{quest_id}"): "Replace a quest's editable fields.",
    ("DELETE", "/api/v1/quests/{quest_id}"): "Delete a quest you are allowed to manage.",
}


@router.get("/api/v1/greeting", response_class=HTMLResponse, tags=["Project"])
def greeting(request: Request) -> HTMLResponse:
    """Show project details and the endpoints currently registered in the app."""
    rows = []
    for path, operations in request.app.openapi()["paths"].items():
        if not path.startswith("/api/v1/"):
            continue
        for operation in operations:
            method = operation.upper()
            if method not in {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}:
                continue
            description = DESCRIPTIONS.get((method, path), "See the API documentation.")
            rows.append(
                f'<tr><td><span class="method">{escape(method)}</span></td>'
                f'<td><code>{escape(path)}</code></td>'
                f'<td>{escape(description)}</td></tr>'
            )
    return HTMLResponse(PAGE.replace("<!-- ENDPOINT_ROWS -->", "\n".join(rows)))
