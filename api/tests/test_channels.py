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

def test_channel_existence(client, auth_headers):
    # Test non-existent channel
    response = client.get("/api/channels/non-existent-channel", headers=auth_headers)
    assert response.status_code == status.HTTP_404_NOT_FOUND

    # Create a channel
    create_response = client.post(
        "/api/channels/",
        headers=auth_headers,
        json={"name": "existence-test-channel"}
    )
    assert create_response.status_code == status.HTTP_200_OK

    # Test existing channel
    response = client.get("/api/channels/existence-test-channel", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "existence-test-channel"

def test_user_subscription_status(client, auth_headers):
    # Create a second user
    client.post(
        "/api/auth/register",
        json={
            "username": "subtest",
            "email": "sub@test.com",
            "password": "testpass123",
            "display_name": "Sub Test"
        }
    )
    
    # Login as second user
    login_response = client.post(
        "/api/auth/login",
        json={
            "username": "subtest",
            "password": "testpass123"
        }
    )
    sub_user_token = login_response.json()["access_token"]
    sub_headers = {"Authorization": f"Bearer {sub_user_token}"}
    
    # Create a channel as first user
    create_response = client.post(
        "/api/channels/",
        headers=auth_headers,
        json={"name": "subscription-test-channel"}
    )
    channel_id = create_response.json()["id"]
    
    # Check subscription status before joining (should be false)
    status_response = client.get(
        f"/api/channels/subscription-test-channel/status",
        headers=sub_headers
    )
    assert status_response.status_code == status.HTTP_200_OK
    assert status_response.json()["is_subscribed"] == False
    
    # Join channel as second user
    join_response = client.post(
        f"/api/channels/subscription-test-channel/join",
        headers=sub_headers
    )
    assert join_response.status_code == status.HTTP_200_OK
    
    # Check subscription status after joining (should be true)
    status_response = client.get(
        f"/api/channels/subscription-test-channel/status",
        headers=sub_headers
    )
    assert status_response.status_code == status.HTTP_200_OK
    assert status_response.json()["is_subscribed"] == True 