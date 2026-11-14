"""Exercise shared handlers through temporary routes, not unfinished quest APIs."""

import pytest
from fastapi import APIRouter, HTTPException, Query
from fastapi.testclient import TestClient
from pydantic import BaseModel, Field

from app.main import app
from app.responses import success_response


class ExampleBody(BaseModel):
    title: str = Field(min_length=3)


@pytest.fixture
def client():
    router = APIRouter()

    @router.post("/_test/items", status_code=201)
    def create_item(body: ExampleBody):
        return success_response("Item created.", body.model_dump())

    @router.get("/_test/items")
    def list_items(page: int = Query(default=1, ge=1)):
        return success_response(
            "Items retrieved.", [], meta={"total": 0, "page": page, "perPage": 10}
        )

    @router.delete("/_test/items/{item_id}")
    def delete_item(item_id: int):
        return success_response("Item deleted.")

    @router.get("/_test/errors/{status}")
    def raise_http_error(status: int):
        raise HTTPException(
            status_code=status,
            detail="Example error.",
            headers={"WWW-Authenticate": "Bearer"} if status == 401 else None,
        )

    @router.get("/_test/crash")
    def crash():
        raise RuntimeError("private database path /srv/private.db")

    original_routes = list(app.router.routes)
    original_schema = app.openapi_schema
    app.include_router(router)
    try:
        with TestClient(app, raise_server_exceptions=False) as test_client:
            yield test_client
    finally:
        app.router.routes[:] = original_routes
        app.openapi_schema = original_schema


def test_application_starts_and_openapi_is_available(client):
    response = client.get("/openapi.json")
    assert response.status_code == 200
    assert response.json()["info"]["title"] == "LifeQuest API"


def test_created_resource_envelope(client):
    response = client.post("/_test/items", json={"title": "Study"})
    assert response.status_code == 201
    assert response.json() == {
        "success": True, "message": "Item created.", "data": {"title": "Study"}
    }


def test_paginated_list_envelope(client):
    response = client.get("/_test/items?page=2")
    assert response.status_code == 200
    assert response.json() == {
        "success": True, "message": "Items retrieved.", "data": [],
        "meta": {"total": 0, "page": 2, "perPage": 10},
    }


def test_delete_envelope_has_null_data(client):
    response = client.delete("/_test/items/1")
    assert response.status_code == 200
    assert response.json()["data"] is None


@pytest.mark.parametrize("body", [{}, {"title": 123}, {"title": "ab"}])
def test_invalid_body_returns_400_and_field_details(client, body):
    response = client.post("/_test/items", json=body)
    assert response.status_code == 400
    result = response.json()
    assert result["success"] is False
    assert result["error"]["code"] == "VALIDATION_ERROR"
    assert result["error"]["details"][0]["field"] == "title"
    assert set(result["error"]["details"][0]) == {"field", "message"}


def test_malformed_json_returns_safe_validation_error(client):
    response = client.post(
        "/_test/items", content='{"title":',
        headers={"Content-Type": "application/json"},
    )
    assert response.status_code == 400
    assert response.json()["error"]["details"] == [
        {"field": "body", "message": "Request body must contain valid JSON."}
    ]


@pytest.mark.parametrize("url, field", [
    ("/_test/items?page=0", "page"),
    ("/_test/items?page=abc", "page"),
])
def test_query_validation(client, url, field):
    response = client.get(url)
    assert response.status_code == 400
    assert response.json()["error"]["details"][0]["field"] == field


def test_path_validation(client):
    response = client.delete("/_test/items/abc")
    assert response.status_code == 400
    assert response.json()["error"]["details"][0]["field"] == "item_id"


@pytest.mark.parametrize("status, code", [
    (400, "BAD_REQUEST"), (401, "UNAUTHORIZED"),
    (403, "FORBIDDEN"), (404, "NOT_FOUND"), (409, "CONFLICT"),
])
def test_http_errors_have_consistent_envelopes(client, status, code):
    response = client.get(f"/_test/errors/{status}")
    assert response.status_code == status
    assert response.json() == {
        "success": False, "error": {"code": code, "message": "Example error."}
    }
    if status == 401:
        assert response.headers["www-authenticate"] == "Bearer"


def test_unknown_route_returns_structured_404(client):
    response = client.get("/missing")
    assert response.status_code == 404
    assert response.json()["error"]["code"] == "NOT_FOUND"
    assert "details" not in response.json()["error"]


def test_unsupported_method_preserves_allow_header(client):
    response = client.put("/_test/items")
    assert response.status_code == 405
    assert response.json()["error"]["code"] == "METHOD_NOT_ALLOWED"
    assert response.headers.get("allow")


@pytest.mark.parametrize("url", ["/_test/crash", "/_test/errors/500"])
def test_server_errors_hide_internal_details(client, url):
    response = client.get(url)
    assert response.status_code == 500
    assert response.json() == {
        "success": False,
        "error": {
            "code": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected server error occurred.",
        },
    }
