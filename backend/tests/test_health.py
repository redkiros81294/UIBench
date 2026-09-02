"""Backend health check tests."""
import pytest
from fastapi.testclient import TestClient

from backend.app.main import create_app


@pytest.fixture()
def client():
    app = create_app()
    with TestClient(app) as client:
        yield client


def test_health_endpoint(client: TestClient):
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "checks" in data
    assert "database" in data["checks"]
