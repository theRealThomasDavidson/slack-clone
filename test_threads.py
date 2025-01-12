"""Test thread functionality."""

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

def test_create_message_with_reply(headers):
    """Test creating a message and replying to it."""
    print("\nTesting create message with reply...")
    # First, create a parent message
    parent_data = {
        "content": "Parent message",
        "channel_id": "1",
    }
    response = requests.post(f"{API_BASE_URL}/messages/", data=parent_data, headers=headers)
    assert response.status_code == 200, "Failed to create parent message"
    parent_message = response.json()
    assert parent_message["content"] == "Parent message", "Parent message content mismatch"
    assert parent_message["reply_count"] == 0, "Initial reply count should be 0"

    # Create a reply to the parent message
    reply_data = {
        "content": "Reply message",
        "channel_id": "1",
        "parent_id": str(parent_message["id"])
    }
    response = requests.post(f"{API_BASE_URL}/messages/", data=reply_data, headers=headers)
    assert response.status_code == 200, "Failed to create reply message"
    reply_message = response.json()
    assert reply_message["content"] == "Reply message", "Reply message content mismatch"
    assert reply_message["parent_id"] == parent_message["id"], "Parent ID mismatch"

    # Get the parent message again to check reply_count
    response = requests.get(f"{API_BASE_URL}/messages/{parent_message['id']}", headers=headers)
    assert response.status_code == 200, "Failed to get updated parent message"
    updated_parent = response.json()
    assert updated_parent["reply_count"] == 1, "Reply count should be 1"
    print("✓ Create message with reply test passed")

def test_get_message_replies(headers):
    """Test getting replies for a message."""
    print("\nTesting get message replies...")
    # Create a parent message
    parent_data = {
        "content": "Parent for replies",
        "channel_id": "1",
    }
    response = requests.post(f"{API_BASE_URL}/messages/", data=parent_data, headers=headers)
    assert response.status_code == 200, "Failed to create parent message"
    parent_message = response.json()

    # Create multiple replies
    reply_contents = ["First reply", "Second reply", "Third reply"]
    for content in reply_contents:
        reply_data = {
            "content": content,
            "channel_id": "1",
            "parent_id": str(parent_message["id"])
        }
        response = requests.post(f"{API_BASE_URL}/messages/", data=reply_data, headers=headers)
        assert response.status_code == 200, f"Failed to create reply: {content}"

    # Get all replies for the parent message
    response = requests.get(f"{API_BASE_URL}/messages/{parent_message['id']}/replies", headers=headers)
    assert response.status_code == 200, "Failed to get replies"
    replies = response.json()
    assert len(replies) == len(reply_contents), "Reply count mismatch"
    assert all(reply["parent_id"] == parent_message["id"] for reply in replies), "Parent ID mismatch in replies"
    print("✓ Get message replies test passed")

def test_invalid_reply_scenarios(headers):
    """Test error cases for message replies."""
    print("\nTesting invalid reply scenarios...")
    # Try to reply to non-existent message
    reply_data = {
        "content": "Reply to nothing",
        "channel_id": "1",
        "parent_id": "99999"
    }
    response = requests.post(f"{API_BASE_URL}/messages/", data=reply_data, headers=headers)
    assert response.status_code == 404, "Should fail with non-existent parent"

    # Create messages in different channels
    channel1_msg = requests.post(f"{API_BASE_URL}/messages/", data={
        "content": "Channel 1 message",
        "channel_id": "1"
    }, headers=headers).json()

    # Try to reply to a message from a different channel
    reply_data = {
        "content": "Cross-channel reply",
        "channel_id": "2",
        "parent_id": str(channel1_msg["id"])
    }
    response = requests.post(f"{API_BASE_URL}/messages/", data=reply_data, headers=headers)
    assert response.status_code == 400, "Should fail with cross-channel reply"
    print("✓ Invalid reply scenarios test passed")

def test_message_thread_ordering(headers):
    """Test that replies are returned in chronological order."""
    print("\nTesting message thread ordering...")
    # Create a parent message
    parent_data = {
        "content": "Parent for ordered replies",
        "channel_id": "1",
    }
    response = requests.post(f"{API_BASE_URL}/messages/", data=parent_data, headers=headers)
    assert response.status_code == 200, "Failed to create parent message"
    parent_message = response.json()

    # Create replies with different timestamps
    reply_contents = ["First", "Second", "Third"]
    for content in reply_contents:
        reply_data = {
            "content": content,
            "channel_id": "1",
            "parent_id": str(parent_message["id"])
        }
        response = requests.post(f"{API_BASE_URL}/messages/", data=reply_data, headers=headers)
        assert response.status_code == 200, f"Failed to create reply: {content}"

    # Get replies and verify order
    response = requests.get(f"{API_BASE_URL}/messages/{parent_message['id']}/replies", headers=headers)
    assert response.status_code == 200, "Failed to get replies"
    replies = response.json()
    
    # Verify replies are in chronological order
    for i in range(len(replies) - 1):
        assert replies[i]["created_at"] <= replies[i + 1]["created_at"], "Replies not in chronological order"
        assert replies[i]["content"] == reply_contents[i], "Reply content mismatch"
    print("✓ Message thread ordering test passed")

def run_all_tests():
    """Run all tests."""
    try:
        print("Logging in...")
        token = login()
        headers = {"Authorization": f"Bearer {token}"}
        
        # Run all tests
        test_create_message_with_reply(headers)
        test_get_message_replies(headers)
        test_invalid_reply_scenarios(headers)
        test_message_thread_ordering(headers)
        
        print("\nAll tests passed! ✨")
    except AssertionError as e:
        print(f"\n❌ Test failed: {str(e)}")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")

if __name__ == "__main__":
    run_all_tests() 