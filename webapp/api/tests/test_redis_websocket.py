import pytest
from fastapi.testclient import TestClient
from ..main import app
from ..utils.redis_manager import RedisManager
from ..services.auth import AuthService
import json
import asyncio
from typing import Dict, List
import websockets
import redis

auth_service = AuthService()

@pytest.fixture
async def test_user_token(test_client):
    """Create a test user and return their token"""
    username = "testuser"
    password = "testpass123"
    email = "test@example.com"
    
    # Create user if doesn't exist
    response = test_client.post(
        "/api/auth/register",
        json={
            "username": username,
            "password": password,
            "email": email,
            "display_name": "Test User"
        }
    )
    
    # Login to get token
    response = test_client.post(
        "/api/auth/login",
        data={
            "username": username,
            "password": password
        }
    )
    assert response.status_code == 200
    return response.json()["access_token"]

async def create_websocket_client(token: str, username: str) -> websockets.WebSocketClientProtocol:
    """Helper function to create a websocket connection"""
    uri = f"ws://localhost:8000/api/ws/{username}?token={token}"
    return await websockets.connect(uri)

@pytest.mark.asyncio
async def test_websocket_connection(test_user_token, redis_manager):
    """Test basic WebSocket connection"""
    async with await create_websocket_client(test_user_token, "testuser") as websocket:
        # Verify connection is established
        assert websocket.open

@pytest.mark.asyncio
async def test_redis_message_broadcast(test_user_token, redis_manager):
    """Test message broadcasting through Redis"""
    async with await create_websocket_client(test_user_token, "testuser") as websocket:
        # Send a message
        message = {
            "content": "Hello Redis!",
            "channel_id": "general"
        }
        await websocket.send(json.dumps(message))
        
        # Receive the broadcasted message
        response = await websocket.recv()
        data = json.loads(response)
        
        assert data["content"] == "Hello Redis!"
        assert data["username"] == "testuser"
        assert "channel_id" in data
        assert "timestamp" in data

@pytest.mark.asyncio
async def test_multiple_clients(test_user_token, test_client, redis_manager):
    """Test message broadcasting to multiple clients"""
    # Create second user
    test_client.post(
        "/api/auth/register",
        json={
            "username": "testuser2",
            "password": "testpass123",
            "email": "test2@example.com",
            "display_name": "Test User 2"
        }
    )
    response = test_client.post(
        "/api/auth/login",
        data={
            "username": "testuser2",
            "password": "testpass123"
        }
    )
    token2 = response.json()["access_token"]
    
    # Connect both users
    async with await create_websocket_client(test_user_token, "testuser") as ws1, \
              await create_websocket_client(token2, "testuser2") as ws2:
        
        # Send message from first user
        message = {
            "content": "Hello everyone!",
            "channel_id": "general"
        }
        await ws1.send(json.dumps(message))
        
        # Both users should receive the message
        response1 = await ws1.recv()
        response2 = await ws2.recv()
        
        data1 = json.loads(response1)
        data2 = json.loads(response2)
        
        assert data1 == data2
        assert data1["content"] == "Hello everyone!"
        assert data1["username"] == "testuser"

@pytest.mark.asyncio
async def test_channel_message_history(test_user_token, test_client, redis_manager):
    """Test message history retrieval from Redis"""
    async with await create_websocket_client(test_user_token, "testuser") as websocket:
        # Send multiple messages
        messages = [
            {"content": f"Message {i}", "channel_id": "general"}
            for i in range(3)
        ]
        
        for msg in messages:
            await websocket.send(json.dumps(msg))
            await websocket.recv()  # Wait for broadcast
        
        # Get channel messages through REST API
        response = test_client.get(
            "/api/messages/general",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        assert response.status_code == 200
        history = response.json()
        
        # Verify messages are in Redis and ordered correctly
        assert len(history) == 3
        assert [msg["content"] for msg in reversed(history)] == [
            "Message 0",
            "Message 1",
            "Message 2"
        ]

@pytest.mark.asyncio
async def test_channel_subscription(test_user_token, test_client, redis_manager):
    """Test channel subscription and message routing"""
    async with await create_websocket_client(test_user_token, "testuser") as websocket:
        # Send message to specific channel
        message = {
            "content": "Channel specific message",
            "channel_id": "random"  # Using 'random' channel
        }
        await websocket.send(json.dumps(message))
        
        # Verify message is received
        response = await websocket.recv()
        data = json.loads(response)
        
        assert data["content"] == "Channel specific message"
        assert data["channel_id"] == "random"
        
        # Verify message is in channel history
        response = test_client.get(
            "/api/channels/random/messages",
            headers={"Authorization": f"Bearer {test_user_token}"}
        )
        
        assert response.status_code == 200
        history = response.json()
        assert len(history) > 0
        assert history[0]["content"] == "Channel specific message"

@pytest.mark.asyncio
async def test_redis_connection_failure(redis_manager):
    """Test system behavior when Redis connection fails"""
    # Save current Redis instance
    original_redis = redis_manager.redis
    
    try:
        # Create a Redis client with invalid connection
        redis_manager.redis = redis.Redis(host='invalid_host', port=6379)
        
        # Attempt to broadcast should not raise exception but log error
        await redis_manager.broadcast_to_channel(
            {"content": "Test message"},
            "general"
        )
    finally:
        # Restore original Redis connection
        redis_manager.redis = original_redis 