import pytest
from fastapi import status

def test_protected_route(client, auth_headers):
    response = client.get("/api/auth/test-auth", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Authentication successful"
    assert data["username"] == "testuser"

def test_get_current_user(client, auth_headers):
    response = client.get("/api/users/me", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "testuser"

def test_get_user_by_username(client, auth_headers):
    response = client.get("/api/users/testuser", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "testuser"

def test_get_all_users(client, auth_headers):
    response = client.get("/api/users/", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) > 0

def test_update_user_profile(client, auth_headers):
    response = client.put(
        "/api/users/me",
        headers=auth_headers,
        json={
            "display_name": "Updated Test User",
            "email": "updated@test.com"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["display_name"] == "Updated Test User"
    assert data["email"] == "updated@test.com"
