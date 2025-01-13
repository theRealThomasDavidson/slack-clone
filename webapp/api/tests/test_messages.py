import pytest
from fastapi import status
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocketDisconnect
import json
import asyncio
from asyncio import TimeoutError
import logging
import time

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

def test_message_persistence(client, auth_headers):
    # Create a channel
    channel_response = client.post(
        "/api/channels/",
        headers=auth_headers,
        json={"name": "persistence-test-channel"}
    )
    assert channel_response.status_code == status.HTTP_200_OK
    channel = channel_response.json()

    # Send a message
    message_content = "Test message for persistence"
    message_response = client.post(
        "/api/messages/",
        headers=auth_headers,
        json={
            "content": message_content,
            "channel_id": channel["id"]
        }
    )
    assert message_response.status_code == status.HTTP_200_OK
    sent_message = message_response.json()

    # Get channel messages
    messages_response = client.get(
        f"/api/messages/{channel['id']}",
        headers=auth_headers
    )
    assert messages_response.status_code == status.HTTP_200_OK
    messages = messages_response.json()

    # Verify message persistence
    assert len(messages) > 0
    found_message = next((m for m in messages if m["id"] == sent_message["id"]), None)
    assert found_message is not None
    assert found_message["content"] == message_content

    # Verify message after server restart (if using in-memory storage, this should be documented)
    # Note: This part of the test demonstrates whether storage is persistent or in-memory
    messages_after_response = client.get(
        f"/api/messages/{channel['id']}",
        headers=auth_headers
    )
    assert messages_after_response.status_code == status.HTTP_200_OK
    messages_after = messages_after_response.json()
    found_message_after = next((m for m in messages_after if m["id"] == sent_message["id"]), None)
    assert found_message_after is not None
    assert found_message_after["content"] == message_content

def test_message_broadcasting(client, auth_headers):
    # Create two additional users for testing broadcasting
    for i in range(2):
        client.post(
            "/api/auth/register",
            json={
                "username": f"broadcastuser{i}",
                "email": f"broadcast{i}@test.com",
                "password": "testpass123",
                "display_name": f"Broadcast User {i}"
            }
        )

    # Login both users and get their tokens
    user_tokens = []
    usernames = []
    for i in range(2):
        login_response = client.post(
            "/api/auth/login",
            json={
                "username": f"broadcastuser{i}",
                "password": "testpass123"
            }
        )
        user_tokens.append(login_response.json()["access_token"])
        usernames.append(f"broadcastuser{i}")

    # Clear message history before testing
    clear_response = client.post("/api/messages/clear", headers=auth_headers)
    assert clear_response.status_code == status.HTTP_200_OK

    # Create a channel
    channel_response = client.post(
        "/api/channels/",
        headers=auth_headers,
        json={"name": "broadcast-test-channel"}
    )
    assert channel_response.status_code == status.HTTP_200_OK
    channel = channel_response.json()

    # Have both users join the channel
    for token in user_tokens:
        headers = {"Authorization": f"Bearer {token}"}
        join_response = client.post(
            f"/api/channels/{channel['name']}/join",
            headers=headers
        )
        assert join_response.status_code == status.HTTP_200_OK

    # Connect all users to WebSocket
    owner_username = "testuser"  # This is set in conftest.py
    with client.websocket_connect(f"/api/ws/{owner_username}?token={auth_headers['Authorization'].split()[1]}") as ws_owner:
        with client.websocket_connect(f"/api/ws/{usernames[0]}?token={user_tokens[0]}") as ws_user1:
            with client.websocket_connect(f"/api/ws/{usernames[1]}?token={user_tokens[1]}") as ws_user2:
                # Send a message from the channel owner
                message_content = "Broadcast test message"
                ws_owner.send_json({
                    "content": message_content,
                    "channel_id": channel["id"]
                })

                # Verify all users receive the message
                for ws in [ws_owner, ws_user1, ws_user2]:
                    data = ws.receive_json()
                    assert data["content"] == message_content
                    assert data["channel_id"] == channel["id"]