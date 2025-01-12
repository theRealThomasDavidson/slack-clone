"""Pytest configuration and fixtures."""

import pytest
import requests

API_BASE_URL = "http://localhost:8000/api/v1"

@pytest.fixture(scope="session")
def auth_token():
    """Get authentication token for tests."""
    login_data = {
        "username": "testuser",
        "password": "testpass"
    }
    response = requests.post(f"{API_BASE_URL}/auth/login", data=login_data)
    assert response.status_code == 200
    token = response.json()["access_token"]
    return token

@pytest.fixture(scope="session")
def auth_headers(auth_token):
    """Get headers with authentication token."""
    return {
        "Authorization": f"Bearer {auth_token}"
    } 