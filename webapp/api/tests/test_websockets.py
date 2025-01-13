import pytest
from fastapi import status
from fastapi.testclient import TestClient
from fastapi.websockets import WebSocketDisconnect
import json
import asyncio
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def test_websocket_real_time_messaging(client):
    """Test real-time messaging between two users in a channel via WebSocket"""
    print("\n=== Starting WebSocket real-time messaging test ===")
    
    # Create and login first user
    print("Creating first user...")
    client.post(
        "/api/auth/register",
        json={
            "username": "wsuser1",
            "email": "ws1@test.com",
            "password": "testpass123",
            "display_name": "WebSocket User 1"
        }
    )
    
    print("Logging in first user...")
    login_response1 = client.post(
        "/api/auth/login",
        json={
            "username": "wsuser1",
            "password": "testpass123"
        }
    )
    user1_token = login_response1.json()["access_token"]
    user1_headers = {"Authorization": f"Bearer {user1_token}"}
    
    # Create and login second user
    print("Creating second user...")
    client.post(
        "/api/auth/register",
        json={
            "username": "wsuser2",
            "email": "ws2@test.com",
            "password": "testpass123",
            "display_name": "WebSocket User 2"
        }
    )
    
    print("Logging in second user...")
    login_response2 = client.post(
        "/api/auth/login",
        json={
            "username": "wsuser2",
            "password": "testpass123"
        }
    )
    user2_token = login_response2.json()["access_token"]
    user2_headers = {"Authorization": f"Bearer {user2_token}"}
    
    # Create a channel
    print("Creating channel...")
    channel_response = client.post(
        "/api/channels/",
        headers=user1_headers,
        json={
            "name": "websocket-test-channel",
            "description": "WebSocket Test Channel"
        }
    )
    assert channel_response.status_code == status.HTTP_200_OK
    channel = channel_response.json()
    
    # Second user joins the channel
    print("Second user joining channel...")
    join_response = client.post(
        f"/api/channels/websocket-test-channel/join",
        headers=user2_headers
    )
    assert join_response.status_code == status.HTTP_200_OK

    # Test WebSocket connections
    print("Testing WebSocket connections...")
    with client.websocket_connect(f"/api/ws/wsuser1?token={user1_token}") as websocket1:
        with client.websocket_connect(f"/api/ws/wsuser2?token={user2_token}") as websocket2:
            # Send a message from user 1
            print("User 1 sending message...")
            websocket1.send_json({
                "content": "Hello from user 1!",
                "channel_id": channel["id"]
            })
            
            # User 1 should receive their own message first
            print("User 1 waiting for own message...")
            data = websocket1.receive_json()
            assert data["content"] == "Hello from user 1!"
            assert data["channel_id"] == channel["id"]
            print("Message received by user 1")
            
            # User 2 should receive user 1's message
            print("User 2 waiting for user 1's message...")
            data = websocket2.receive_json()
            assert data["content"] == "Hello from user 1!"
            assert data["channel_id"] == channel["id"]
            print("Message received by user 2")
                
            # Send a message from user 2
            print("User 2 sending message...")
            websocket2.send_json({
                "content": "Hello back from user 2!",
                "channel_id": channel["id"]
            })
            
            # User 2 should receive their own message first
            print("User 2 waiting for own message...")
            data = websocket2.receive_json()
            assert data["content"] == "Hello back from user 2!"
            assert data["channel_id"] == channel["id"]
            print("Message received by user 2")
            
            # User 1 should receive user 2's message
            print("User 1 waiting for user 2's message...")
            data = websocket1.receive_json()
            assert data["content"] == "Hello back from user 2!"
            assert data["channel_id"] == channel["id"]
            print("Message received by user 1")

    print("Test completed successfully") 