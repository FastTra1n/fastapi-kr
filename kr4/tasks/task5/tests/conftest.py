import pytest
from faker import Faker
from httpx import AsyncClient, ASGITransport

from app import app, users

fake = Faker()

@pytest.fixture(autouse=True)
def clear_db():
    users.clear()
    yield

@pytest.fixture
async def async_client():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://127.0.0.1:8000") as client:
        yield client

@pytest.fixture
def fake_user_data():
    return {
        "username": fake.user_name(),
        "password": fake.password()
    }