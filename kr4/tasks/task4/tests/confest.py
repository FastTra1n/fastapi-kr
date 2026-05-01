import pytest
from fastapi.testclient import TestClient

from app import app, users

@pytest.fixture
def client():
    return TestClient(app)