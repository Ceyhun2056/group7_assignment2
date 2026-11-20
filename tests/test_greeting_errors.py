"""Additional checks for greeting links, endpoint listings, and HTTP errors."""

from html import escape

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_invalid_token_does_not_protect_the_public_greeting(client):
    response = client.get(
        "/api/v1/greeting", headers={"Authorization": "Bearer invalid-token"}
    )
    assert response.status_code == 200
    assert response.headers["content-type"] == "text/html; charset=utf-8"
    assert "LifeQuest" in response.text


def test_documentation_link_works(client):
    response = client.get("/api/v1/greeting")
    assert '<a href="/docs">' in response.text
    assert client.get("/docs").status_code == 200


def test_endpoint_table_pairs_each_method_with_its_path_once(client):
    html = client.get("/api/v1/greeting").text
    paths = client.get("/openapi.json").json()["paths"]
    expected_rows = 0
    for path, operations in paths.items():
        if not path.startswith("/api/v1/"):
            continue
        for method in operations:
            if method.upper() not in {"GET", "POST", "PUT", "DELETE", "PATCH", "HEAD", "OPTIONS"}:
                continue
            expected_rows += 1
            row_start = (
                f'<tr><td><span class="method">{method.upper()}</span></td>'
                f'<td><code>{escape(path)}</code></td>'
            )
            assert html.count(row_start) == 1
    assert expected_rows >= 3
    assert html.count('<tr><td><span class="method">') == expected_rows


@pytest.mark.parametrize("method", ["POST", "PUT", "DELETE", "PATCH"])
def test_greeting_rejects_unsupported_methods_with_structured_405(client, method):
    response = client.request(method, "/api/v1/greeting")
    assert response.status_code == 405
    assert response.headers["content-type"] == "application/json"
    assert "GET" in response.headers["allow"].split(", ")
    assert response.json() == {
        "success": False,
        "error": {"code": "METHOD_NOT_ALLOWED", "message": "Method Not Allowed"},
    }


@pytest.mark.parametrize("method", ["GET", "POST"])
def test_unknown_api_path_returns_structured_404(client, method):
    response = client.request(method, "/api/v1/nonexistent-endpoint")
    assert response.status_code == 404
    assert response.headers["content-type"] == "application/json"
    assert response.json() == {
        "success": False,
        "error": {"code": "NOT_FOUND", "message": "Not Found"},
    }
