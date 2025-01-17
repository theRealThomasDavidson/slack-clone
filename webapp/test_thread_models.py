"""Test thread-related models."""

import requests
import json
from datetime import datetime

API_BASE_URL = "http://localhost:8000/api/v1"

def login():
    """Login and return the auth token."""
    login_data = {
        "username": "testuser",
        "password": "testpass"
    }
    response = requests.post(f"{API_BASE_URL}/auth/login", data=login_data)
    if response.status_code != 200:
        raise Exception("Failed to login")
    return response.json()["access_token"]

def test_message_parent_relationship(headers):
    """Test parent-child relationship between messages."""
    print("\nTesting message parent relationship...")
    # Create parent message
    parent_data = {
        "content": "Parent message",
        "channel_id": "1"
    }
    response = requests.post(f"{API_BASE_URL}/messages/", data=parent_data, headers=headers)
    assert response.status_code == 200, "Failed to create parent message"
    parent = response.json()

    # Create child message
    child_data = {
        "content": "Child message",
        "channel_id": "1",
        "parent_id": str(parent["id"])
    }
    response = requests.post(f"{API_BASE_URL}/messages/", data=child_data, headers=headers)
    assert response.status_code == 200, "Failed to create child message"
    child = response.json()

    # Verify relationships
    assert child["parent_id"] == parent["id"], "Parent-child relationship mismatch"
    
    # Get parent message to verify reply count
    response = requests.get(f"{API_BASE_URL}/messages/{parent['id']}", headers=headers)
    updated_parent = response.json()
    assert updated_parent["reply_count"] == 1, "Reply count should be 1"
    print("✓ Message parent relationship test passed")

def test_message_timestamps(headers):
    """Test that message timestamps are set correctly."""
    print("\nTesting message timestamps...")
    # Create a message
    message_data = {
        "content": "Test timestamps",
        "channel_id": "1"
    }
    response = requests.post(f"{API_BASE_URL}/messages/", data=message_data, headers=headers)
    assert response.status_code == 200, "Failed to create message"
    message = response.json()

    # Verify timestamps exist
    assert "created_at" in message, "Missing created_at timestamp"
    assert "updated_at" in message, "Missing updated_at timestamp"
    created_at = datetime.fromisoformat(message["created_at"].replace("Z", "+00:00"))
    updated_at = datetime.fromisoformat(message["updated_at"].replace("Z", "+00:00"))
    
    # Timestamps should be equal for a new message
    assert created_at == updated_at, "Created and updated timestamps should match for new message"
    print("✓ Message timestamps test passed")

def test_reply_count(headers):
    """Test getting reply count for a message."""
    print("\nTesting reply count...")
    # Create parent message
    parent_data = {
        "content": "Parent for counting",
        "channel_id": "1"
    }
    response = requests.post(f"{API_BASE_URL}/messages/", data=parent_data, headers=headers)
    assert response.status_code == 200, "Failed to create parent message"
    parent = response.json()
    
    # Initially should have no replies
    assert parent["reply_count"] == 0, "Initial reply count should be 0"

    # Add multiple replies
    reply_count = 3
    for i in range(reply_count):
        reply_data = {
            "content": f"Reply {i}",
            "channel_id": "1",
            "parent_id": str(parent["id"])
        }
        response = requests.post(f"{API_BASE_URL}/messages/", data=reply_data, headers=headers)
        assert response.status_code == 200, f"Failed to create reply {i}"

    # Get parent message to verify final reply count
    response = requests.get(f"{API_BASE_URL}/messages/{parent['id']}", headers=headers)
    updated_parent = response.json()
    assert updated_parent["reply_count"] == reply_count, f"Reply count should be {reply_count}"
    print("✓ Reply count test passed")

def run_all_tests():
    """Run all tests."""
    try:
        print("Logging in...")
        token = login()
        headers = {"Authorization": f"Bearer {token}"}
        
        # Run all tests
        test_message_parent_relationship(headers)
        test_message_timestamps(headers)
        test_reply_count(headers)
        
        print("\nAll tests passed! ✨")
    except AssertionError as e:
        print(f"\n❌ Test failed: {str(e)}")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    run_all_tests() 