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

def test_ban_by_username(client, auth_headers):
    """Test banning a user by username"""
    # Create a second user to ban
    client.post(
        "/api/auth/register",
        json={
            "username": "bantest",
            "email": "ban@test.com",
            "password": "testpass123",
            "display_name": "Ban Test"
        }
    )
    
    # Create a channel as first user
    channel_response = client.post(
        "/api/channels/",
        headers=auth_headers,
        json={"name": "ban-test-channel"}
    )
    assert channel_response.status_code == status.HTTP_200_OK
    
    # Ban the second user by username
    ban_response = client.post(
        f"/api/channels/ban-test-channel/ban-by-username/bantest",
        headers=auth_headers
    )
    assert ban_response.status_code == status.HTTP_200_OK
    
    # Verify user is banned
    channel = ban_response.json()
    assert "bantest" in [user["username"] for user in client.get(
        "/api/channels/ban-test-channel/banned-users",
        headers=auth_headers
    ).json()]

def test_cannot_ban_self(client, auth_headers):
    """Test that users cannot ban themselves"""
    # Create a channel
    client.post(
        "/api/channels/",
        headers=auth_headers,
        json={"name": "self-ban-test"}
    )
    
    # Try to ban self
    response = client.post(
        f"/api/channels/self-ban-test/ban-by-username/testuser",  # testuser is the default test user
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "cannot ban yourself" in response.json()["detail"].lower()

def test_cannot_ban_nonexistent_user(client, auth_headers):
    """Test that banning a nonexistent user fails appropriately"""
    # Create a channel
    client.post(
        "/api/channels/",
        headers=auth_headers,
        json={"name": "nonexistent-ban-test"}
    )
    
    # Try to ban nonexistent user
    response = client.post(
        f"/api/channels/nonexistent-ban-test/ban-by-username/nonexistentuser",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_404_NOT_FOUND
    assert "user not found" in response.json()["detail"].lower()

def test_unban_by_username(client, auth_headers):
    """Test unbanning a user by username"""
    # Create a second user to ban/unban
    client.post(
        "/api/auth/register",
        json={
            "username": "unbantest",
            "email": "unban@test.com",
            "password": "testpass123",
            "display_name": "Unban Test"
        }
    )
    
    # Create a channel
    client.post(
        "/api/channels/",
        headers=auth_headers,
        json={"name": "unban-test-channel"}
    )
    
    # Ban the user
    client.post(
        f"/api/channels/unban-test-channel/ban-by-username/unbantest",
        headers=auth_headers
    )
    
    # Unban the user
    unban_response = client.post(
        f"/api/channels/unban-test-channel/unban-by-username/unbantest",
        headers=auth_headers
    )
    assert unban_response.status_code == status.HTTP_200_OK
    
    # Verify user is not in banned users list
    banned_users = client.get(
        "/api/channels/unban-test-channel/banned-users",
        headers=auth_headers
    ).json()
    assert "unbantest" not in [user["username"] for user in banned_users]

def test_get_banned_users(client, auth_headers):
    """Test getting list of banned users"""
    # Create multiple users to ban
    users = ["banlist1", "banlist2", "banlist3"]
    for username in users:
        client.post(
            "/api/auth/register",
            json={
                "username": username,
                "email": f"{username}@test.com",
                "password": "testpass123",
                "display_name": username.title()
            }
        )
    
    # Create a channel
    client.post(
        "/api/channels/",
        headers=auth_headers,
        json={"name": "banlist-test-channel"}
    )
    
    # Ban all test users
    for username in users:
        client.post(
            f"/api/channels/banlist-test-channel/ban-by-username/{username}",
            headers=auth_headers
        )
    
    # Get banned users list
    response = client.get(
        "/api/channels/banlist-test-channel/banned-users",
        headers=auth_headers
    )
    assert response.status_code == status.HTTP_200_OK
    banned_users = response.json()
    
    # Verify all test users are in the banned list
    banned_usernames = [user["username"] for user in banned_users]
    for username in users:
        assert username in banned_usernames

def test_non_owner_cannot_view_banned_users(client, auth_headers):
    """Test that non-owners cannot view banned users list"""
    # Create a second user
    client.post(
        "/api/auth/register",
        json={
            "username": "nonowner",
            "email": "nonowner@test.com",
            "password": "testpass123",
            "display_name": "Non Owner"
        }
    )
    
    # Login as second user
    login_response = client.post(
        "/api/auth/login",
        json={
            "username": "nonowner",
            "password": "testpass123"
        }
    )
    nonowner_token = login_response.json()["access_token"]
    nonowner_headers = {"Authorization": f"Bearer {nonowner_token}"}
    
    # Create a channel as first user
    client.post(
        "/api/channels/",
        headers=auth_headers,
        json={"name": "owner-only-test"}
    )
    
    # Try to view banned users as non-owner
    response = client.get(
        "/api/channels/owner-only-test/banned-users",
        headers=nonowner_headers
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN
    assert "only channel owner" in response.json()["detail"].lower() 