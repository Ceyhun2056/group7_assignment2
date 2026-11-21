"""Keep Swagger validation statuses aligned with the actual handlers."""

from fastapi.testclient import TestClient

from app.main import app


def test_swagger_documents_400_instead_of_automatic_422():
    with TestClient(app) as client:
        schema = client.get("/openapi.json").json()
        response = client.post(
            "/api/v1/quests", json={},
            headers={"Authorization": "Bearer user-a-token"},
        )
    assert response.status_code == 400
    assert response.json()["error"]["code"] == "VALIDATION_ERROR"
    for method in ("get", "post"):
        responses = schema["paths"]["/api/v1/quests"][method]["responses"]
        assert "400" in responses
        assert "422" not in responses
    responses = schema["paths"]["/api/v1/quests/{quest_id}"]["put"]["responses"]
    assert "400" in responses
    assert "422" not in responses
