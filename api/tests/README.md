# Tests Documentation

## Overview

The test suite uses pytest and provides comprehensive testing for all API functionality.

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures and configuration
├── test_auth.py            # Authentication tests
├── test_channels.py        # Channel operations tests
├── test_chat.py           # Chat functionality tests
├── test_files.py          # File upload/download tests
├── test_users.py          # User management tests
└── test_websocket.py      # WebSocket functionality tests
```

## Test Fixtures (`conftest.py`)

Common test fixtures used across test files.

```python
@pytest.fixture
async def client():
    """Test client fixture"""
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client

@pytest.fixture
async def test_db():
    """Test database fixture"""
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def auth_headers(client):
    """Authentication headers fixture"""
    user_data = {
        "username": "testuser",
        "password": "testpass",
        "email": "test@example.com"
    }
    response = await client.post("/api/auth/register", json=user_data)
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
```

## Authentication Tests (`test_auth.py`)

Tests for user authentication functionality.

```python
async def test_register_user(client):
    """Test user registration"""
    response = await client.post(
        "/api/auth/register",
        json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data

async def test_login_user(client):
    """Test user login"""
    response = await client.post(
        "/api/auth/login",
        json={
            "username": "testuser",
            "password": "testpass"
        }
    )
    assert response.status_code == 200
    assert "access_token" in response.json()
```

## Channel Tests (`test_channels.py`)

Tests for channel operations.

```python
async def test_create_channel(client, auth_headers):
    """Test channel creation"""
    response = await client.post(
        "/api/channels",
        headers=auth_headers,
        json={
            "name": "test-channel",
            "description": "Test channel"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "test-channel"

async def test_list_channels(client, auth_headers):
    """Test channel listing"""
    response = await client.get(
        "/api/channels",
        headers=auth_headers
    )
    assert response.status_code == 200
    assert isinstance(response.json(), list)
```

## WebSocket Tests (`test_websocket.py`)

Tests for WebSocket functionality.

```python
async def test_websocket_connection(client, auth_headers):
    """Test WebSocket connection"""
    token = auth_headers["Authorization"].split()[1]
    async with client.websocket_connect(
        f"/api/ws/testuser?token={token}"
    ) as websocket:
        data = await websocket.receive_json()
        assert data["type"] == "connection_established"

async def test_message_broadcast(client, auth_headers):
    """Test message broadcasting"""
    async with client.websocket_connect(
        f"/api/ws/testuser?token={token}"
    ) as websocket:
        await websocket.send_json({
            "type": "message",
            "channel_id": "test-channel",
            "content": "Hello, World!"
        })
        response = await websocket.receive_json()
        assert response["type"] == "message"
        assert response["data"]["content"] == "Hello, World!"
```

## Running Tests

### Run All Tests
```bash
pytest
```

### Run Specific Test File
```bash
pytest tests/test_auth.py
```

### Run with Coverage Report
```bash
pytest --cov=api tests/
```

### Run Tests in Parallel
```bash
pytest -n auto
```

## Test Configuration (`pytest.ini`)

```ini
[pytest]
asyncio_mode = auto
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
filterwarnings =
    ignore::DeprecationWarning
    ignore::UserWarning
``` 