import pytest
from fastapi.testclient import TestClient

from app import app, db, next_id

@pytest.fixture
def client():
    return TestClient(app)

@pytest.fixture(autouse=True)
def clear_db():
    global db, next_id
    db.clear()
    next_id = 1
    yield
