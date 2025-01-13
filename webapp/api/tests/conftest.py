import pytest
import asyncio
import redis
from fastapi.testclient import TestClient
from ..utils.redis_manager import RedisManager
from ..core.config import settings
from ..main import app

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def redis_client():
    """Create a Redis client for testing."""
    client = redis.Redis(
        host=settings.REDIS_HOST,
        port=settings.REDIS_PORT,
        db=0,  # Use a different DB for testing
        decode_responses=True
    )
    yield client
    client.flushdb()  # Clean up after tests
    client.close()

@pytest.fixture(autouse=True)
def clean_redis(redis_client):
    """Clean Redis before each test."""
    redis_client.flushdb()

@pytest.fixture
async def redis_manager(redis_client):
    """Create a RedisManager instance for testing."""
    manager = RedisManager()
    await manager.initialize()
    yield manager
    await manager.close()

@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)

@pytest.fixture
def test_client(client):
    """Create a test client that can be used in async tests."""
    return client

@pytest.fixture
def test_user_token(client):
    """Create a test user and return their token."""
    response = client.post(
        "/api/auth/register",
        json={
            "username": "testuser",
            "email": "test@example.com",
            "password": "testpass123",
            "display_name": "Test User"
        }
    )
    return response.json()["access_token"]

@pytest.fixture
def auth_headers(test_user_token):
    """Create authorization headers for the test user."""
    return {"Authorization": f"Bearer {test_user_token}"} 