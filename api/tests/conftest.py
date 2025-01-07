import pytest
from fastapi.testclient import TestClient
from ..main import app
import asyncio

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for the test session."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
def client():
    with TestClient(app) as client:
        yield client

@pytest.fixture
def auth_headers(client):
    # Register a test user
    client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "display_name": "Test User"
        }
    )
    
    # Login to get the token
    response = client.post(
        "/api/auth/login",
        json={
            "username": "testuser",
            "password": "testpass123"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"} 