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
    yield
    redis_client.flushdb()

@pytest.fixture
async def redis_manager():
    """Get the Redis manager instance with async initialization."""
    manager = RedisManager()
    await manager.initialize()
    yield manager
    await manager.cleanup()

@pytest.fixture
def client():
    """Get the FastAPI test client."""
    with TestClient(app) as client:
        yield client

@pytest.fixture
async def test_client(client):
    """Get an async test client."""
    yield client 