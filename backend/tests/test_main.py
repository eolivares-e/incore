from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_read_root():
    """Test root endpoint."""
    response = client.get("/")
    assert response.status_code == 200

    data = response.json()
    assert data["message"] == "Insurance Core API"
    assert data["version"] == "0.1.0"
    assert "docs" in data


def test_health_check():
    """Test health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "healthy"
    assert data["version"] == "0.1.0"


def test_openapi_docs():
    """Test that OpenAPI docs are accessible."""
    response = client.get("/api/v1/docs")
    assert response.status_code == 200


def test_openapi_json():
    """Test that OpenAPI JSON is accessible."""
    response = client.get("/api/v1/openapi.json")
    assert response.status_code == 200

    data = response.json()
    assert "openapi" in data
    assert data["info"]["title"] == "Insurance Core API"
