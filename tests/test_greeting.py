"""Smoke checks for the public HTML greeting page."""

from fastapi.testclient import TestClient

from app.main import app


def test_greeting_is_public_html_with_required_sections():
    with TestClient(app) as client:
        response = client.get("/api/v1/greeting")
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    for text in ["LifeQuest", "students", "Jeyhun Naghiyev", "21070",
                 "Mahammad Mammadli", "API running", "v1", "Available API endpoints"]:
        assert text in response.text
    assert '<meta name="viewport"' in response.text
    assert "@media" in response.text
    assert "<!-- ENDPOINT_ROWS -->" not in response.text


def test_greeting_lists_all_registered_api_routes():
    with TestClient(app) as client:
        response = client.get("/api/v1/greeting")
    for path in ["/api/v1/greeting", "/api/v1/quests", "/api/v1/quests/{quest_id}"]:
        assert f"<code>{path}</code>" in response.text
    for path, operations in app.openapi()["paths"].items():
        if path.startswith("/api/v1/"):
            assert f"<code>{path}</code>" in response.text
            for method in operations:
                assert f'class="method">{method.upper()}</span>' in response.text
