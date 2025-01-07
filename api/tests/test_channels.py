import pytest
from fastapi import status

def test_protected_route(client, auth_headers):
    response = client.get("/api/auth/test-auth", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Authentication successful"
    assert data["username"] == "testuser"

def test_create_channel(client, auth_headers):
    response = client.post(
        "/api/channels/",
        headers=auth_headers,
        json={
            "name": "test-channel",
            "description": "Test Channel Description"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "test-channel"
    assert "id" in data

def test_get_channels(client, auth_headers):
    # Create a channel first
    client.post(
        "/api/channels/",
        headers=auth_headers,
        json={"name": "list-test-channel"}
    )

    # Get channels
    response = client.get("/api/channels/", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    assert len(response.json()) > 0

def test_join_channel(client, auth_headers):
    # Create a channel first
    client.post(
        "/api/channels/",
        headers=auth_headers,
        json={"name": "join-test-channel"}
    )
    
    # Join channel
    response = client.post(
        f"/api/channels/join-test-channel/join",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["members"]) > 0

def test_leave_channel(client, auth_headers):
    # Create a second user for testing leave functionality
    client.post(
        "/api/auth/register",
        json={
            "username": "leavetest",
            "email": "leave@test.com",
            "password": "testpass123",
            "display_name": "Leave Test"
        }
    )
    
    # Login as second user
    login_response = client.post(
        "/api/auth/login",
        json={
            "username": "leavetest",
            "password": "testpass123"
        }
    )
    leave_user_token = login_response.json()["access_token"]
    leave_headers = {"Authorization": f"Bearer {leave_user_token}"}
    
    # Create a channel as first user
    client.post(
        "/api/channels/",
        headers=auth_headers,
        json={"name": "leave-test-channel"}
    )
    
    # Join channel as second user
    client.post(
        f"/api/channels/leave-test-channel/join",
        headers=leave_headers
    )
    
    # Leave channel as second user
    response = client.post(
        f"/api/channels/leave-test-channel/leave",
        headers=leave_headers
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data["members"]) == 1  # Only the owner should remain 