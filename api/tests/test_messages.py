import pytest
from fastapi import status
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocketDisconnect
import json
import asyncio
from asyncio import TimeoutError
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_protected_route(client, auth_headers):
    logger.info("Starting protected route test")
    response = client.get("/api/auth/test-auth", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Authentication successful"
    assert data["username"] == "testuser"
    logger.info("Protected route test completed")


def test_create_message(client, auth_headers):
    # First create a channel
    channel_response = client.post(
        "/api/channels/",
        headers=auth_headers,
        json={
            "name": "message-test-channel",
            "description": "Test Channel"
        }
    )
    assert channel_response.status_code == status.HTTP_200_OK
    channel_id = channel_response.json()["id"]
    
    # Create message
    response = client.post(
        "/api/messages/",
        headers=auth_headers,
        json={
            "content": "Test message",
            "channel_id": channel_id
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["content"] == "Test message"
    assert data["channel_id"] == channel_id

def test_get_channel_messages(client, auth_headers):
    # First create a channel
    channel_response = client.post(
        "/api/channels/",
        headers=auth_headers,
        json={
            "name": "message-list-channel",
            "description": "Test Channel"
        }
    )
    assert channel_response.status_code == status.HTTP_200_OK
    channel_id = channel_response.json()["id"]
    
    # Create a message
    message_response = client.post(
        "/api/messages/",
        headers=auth_headers,
        json={
            "content": "Test message for listing",
            "channel_id": channel_id
        }
    )
    assert message_response.status_code == status.HTTP_200_OK
    
    # Get messages
    response = client.get(f"/api/messages/{channel_id}", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_get_messages(client, auth_headers):
    response = client.get("/api/messages", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

def test_get_user_messages(client, auth_headers):
    response = client.get("/api/messages/me", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert isinstance(response.json(), list)

@pytest.mark.asyncio
async def test_channel_specific_messaging(client, auth_headers):
    """Test that messages are properly sent to channels"""
    print("\n=== Starting channel messaging test ===")
    
    # Create and login second user
    print("Creating second user...")
    client.post(
        "/api/auth/register",
        json={
            "username": "testuser2",
            "email": "test2@test.com",
            "password": "testpass123",
            "display_name": "Test User 2"
        }
    )
    
    print("Logging in second user...")
    login_response = client.post(
        "/api/auth/login",
        json={
            "username": "testuser2",
            "password": "testpass123"
        }
    )
    user2_token = login_response.json()["access_token"]
    user2_headers = {"Authorization": f"Bearer {user2_token}"}
    
    # Create a channel
    print("Creating channel...")
    channel_response = client.post(
        "/api/channels/",
        headers=auth_headers,
        json={
            "name": "test-broadcast-channel",
            "description": "Test Channel"
        }
    )
    assert channel_response.status_code == status.HTTP_200_OK
    channel = channel_response.json()
    
    # Second user joins the channel
    print("Second user joining channel...")
    join_response = client.post(
        f"/api/channels/test-broadcast-channel/join",
        headers=user2_headers
    )
    assert join_response.status_code == status.HTTP_200_OK

    # Clear message history
    print("Clearing message history...")
    clear_response = client.post("/api/messages/clear", headers=auth_headers)
    assert clear_response.status_code == status.HTTP_200_OK

    # Send a message to the channel
    print("Sending test message...")
    response = client.post(
        "/api/messages/",
        headers=auth_headers,
        json={
            "content": "Test channel message",
            "channel_id": channel["id"]
        }
    )
    assert response.status_code == status.HTTP_200_OK
    print("Message sent successfully")

    # Verify both users can get the message
    print("Checking first user can see message...")
    response1 = client.get(f"/api/messages/{channel['id']}", headers=auth_headers)
    assert response1.status_code == status.HTTP_200_OK
    messages1 = response1.json()
    assert len(messages1) == 1
    assert messages1[0]["content"] == "Test channel message"

    print("Checking second user can see message...")
    response2 = client.get(f"/api/messages/{channel['id']}", headers=user2_headers)
    assert response2.status_code == status.HTTP_200_OK
    messages2 = response2.json()
    assert len(messages2) == 1
    assert messages2[0]["content"] == "Test channel message"

    print("Test completed successfully")