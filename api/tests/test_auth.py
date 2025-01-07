import pytest
from fastapi import status

def test_register_user(client):
    response = client.post(
        "/api/auth/register",
        json={
            "username": "newuser",
            "email": "new@example.com",
            "password": "password123",
            "display_name": "New User"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "newuser"
    assert "id" in data
    assert "email" in data
    assert "created_at" in data
    assert "is_online" in data
    assert "hashed_password" not in data

def test_login_success(client):
    # First register a user
    client.post(
        "/api/auth/register",
        json={
            "username": "logintest",
            "email": "login@test.com",
            "password": "testpass123",
            "display_name": "Login Test"
        }
    )
    
    # Then try to login
    response = client.post(
        "/api/auth/login",
        json={
            "username": "logintest",
            "password": "testpass123"
        }
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_invalid_credentials(client):
    response = client.post(
        "/api/auth/login",
        json={
            "username": "testuser",
            "password": "wrongpass"
        }
    )
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_logout(client):
    # Register and login
    client.post(
        "/api/auth/register",
        json={
            "username": "logouttest",
            "email": "logout@test.com",
            "password": "testpass123",
            "display_name": "Logout Test"
        }
    )
    
    # Login
    login_response = client.post(
        "/api/auth/login",
        json={
            "username": "logouttest",
            "password": "testpass123"
        }
    )
    token = login_response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    
    # Logout
    response = client.post("/api/auth/logout", headers=headers)
    assert response.status_code == status.HTTP_200_OK

def test_protected_route(client, auth_headers):
    response = client.get("/api/auth/test-auth", headers=auth_headers)
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["message"] == "Authentication successful"
    assert data["username"] == "testuser" 