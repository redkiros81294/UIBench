"""Backend test configuration and helpers."""
import os
import sys
import pytest
from fastapi.testclient import TestClient

# Ensure backend/ is importable as `backend`
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.app.main import create_app  # noqa: E402
from backend.database.connection import db_instance  # noqa: E402


@pytest.fixture()
def client():
    app = create_app()
    with TestClient(app) as client:
        yield client
