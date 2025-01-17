import requests
from datetime import datetime
import os
from pathlib import Path
from dotenv import load_dotenv
from .auth import login_user

# Get the rag-project root directory and load .env
RAG_PROJECT_ROOT = Path(__file__).parent.parent.parent
load_dotenv(RAG_PROJECT_ROOT / '.env')

def get_all_channels(auth_token=None, chat_app_url=None):
    """
    Retrieve all available channels.
    If auth_token is not provided, will attempt to login using env credentials.
    """
    if chat_app_url is None:
        chat_app_url = os.getenv('chat_app_url')
    
    # Get auth token if not provided
    if auth_token is None:
        auth_token = login_user(
            chat_app_url=chat_app_url,
            chat_app_username=os.getenv("chat_app_username"),
            chat_app_password=os.getenv("chat_app_password")
        )
        if auth_token is None:
            print("Failed to get authentication token")
            return None
    
    url = f"{chat_app_url.rstrip('/')}/api/v1/channels"
    
    headers = {
        "Authorization": auth_token
    }
    
    print(f"Retrieving all channels")
    try:
        response = requests.get(url, headers=headers)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve channels: {e}")
        return None

def get_channel_messages(channel_id, auth_token=None, chat_app_url=None):
    """
    Retrieve all messages from a specific channel.
    If auth_token is not provided, will attempt to login using env credentials.
    """
    if chat_app_url is None:
        chat_app_url = os.getenv('chat_app_url')
    
    # Get auth token if not provided
    if auth_token is None:
        auth_token = login_user(
            chat_app_url=chat_app_url,
            chat_app_username=os.getenv("JESSE_USERNAME"),
            chat_app_password=os.getenv("JESSE_PASSWORD")
        )
        if auth_token is None:
            print("Failed to get authentication token")
            return None
    
    url = f"{chat_app_url.rstrip('/')}/api/v1/messages/channel/{channel_id}"
    
    headers = {
        "Authorization": auth_token
    }
    
    print(f"Retrieving messages from channel {channel_id}")
    try:
        response = requests.get(url, headers=headers)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve messages: {e}")
        return None

def get_message_replies(message_id, auth_token=None, chat_app_url=None):
    """
    Retrieve all replies for a specific message.
    """
    if chat_app_url is None:
        chat_app_url = os.getenv('chat_app_url')
    
    url = f"{chat_app_url.rstrip('/')}/api/v1/messages/thread/{message_id}"
    
    headers = {
        "Authorization": auth_token
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve replies for message {message_id}: {e}")
        return None

def print_message_tree(messages, auth_token, chat_app_url, indent=0):
    """
    Recursively print messages and their replies with proper indentation.
    """
    for msg in messages:
        # Print the current message with indentation
        print("    " * indent + f"- {msg.get('content', 'No content')} (by {msg.get('username', 'Unknown')})")
        
        # Get and print replies if any exist
        if msg.get('replies_count', 0) > 0:
            replies = get_message_replies(msg['id'], auth_token, chat_app_url)
            if replies:
                print_message_tree(replies, auth_token, chat_app_url, indent + 1)

def get_user_messages(username, auth_token=None, chat_app_url=None):
    """Get all messages from a specific user."""
    if not auth_token:
        chat_app_url = os.getenv('chat_app_url')
        auth_token = login_user(
            chat_app_url=chat_app_url,
            chat_app_username=os.getenv("JESSE_USERNAME"),
            chat_app_password=os.getenv("JESSE_PASSWORD")
        )
    if not chat_app_url:
        chat_app_url = os.getenv('chat_app_url')
    
    # Fix: Add 'Bearer' prefix if it's not already there
    if auth_token and not auth_token.startswith('Bearer '):
        auth_token = f'Bearer {auth_token}'
    
    headers = {
        'Authorization': auth_token
    }
    
    # First get all channels
    channels_url = f"{chat_app_url.rstrip('/')}/api/v1/channels"
    print(f"Fetching channels to find messages from user {username}")
    
    try:
        channels_response = requests.get(channels_url, headers=headers)
        channels_response.raise_for_status()
        channels = channels_response.json()
        
        all_messages = []
        # Get messages from each channel
        for channel in channels:
            channel_url = f"{chat_app_url.rstrip('/')}/api/v1/messages/channel/{channel['id']}"
            messages_response = requests.get(channel_url, headers=headers)
            if messages_response.status_code == 200:
                channel_messages = messages_response.json()
                # Filter messages by username
                user_messages = [msg for msg in channel_messages if msg.get('username') == username]
                all_messages.extend(user_messages)
        
        return all_messages
    except requests.exceptions.RequestException as e:
        print(f"Error fetching messages: {str(e)}")
        return None

def print_user_messages(username, auth_token=None, chat_app_url=None):
    """Print all messages from a specific user in a readable format."""
    messages = get_user_messages(username, auth_token, chat_app_url)
    if not messages:
        print(f"No messages found for user {username}")
        return
    
    print(f"\nMessages from {username}:")
    print("-" * 50)
    
    for message in messages:
        # Format timestamp
        created_at = datetime.fromisoformat(message['created_at'].replace('Z', '+00:00'))
        formatted_time = created_at.strftime('%Y-%m-%d %H:%M:%S')
        
        # Get channel info if available
        channel_context = f"in channel {message['channel_id']}" if message['channel_id'] else "in DM"
        
        # Format message header
        print(f"{formatted_time} {channel_context}:")
        print(f"{message['content']}")
        
        # Show file attachment if present
        if message['file']:
            print(f"[Attached file: {message['file']['filename']}]")
        
        # Show reactions if present
        if message['emojis']:
            reactions = [f"{emoji}: {', '.join(users)}" for emoji, users in message['emojis'].items()]
            print(f"Reactions: {' | '.join(reactions)}")
        
        # Show reply count if there are replies
        if message.get('replies_count', 0) > 0:
            print(f"Replies: {message['replies_count']}")
        
        print("-" * 50)

def get_all_users(auth_token=None, chat_app_url=None):
    """
    Retrieve all users with their online status.
    If auth_token is not provided, will attempt to login using env credentials.
    """
    if chat_app_url is None:
        chat_app_url = os.getenv('chat_app_url')
    
    # Get auth token if not provided
    if auth_token is None:
        auth_token = login_user(
            chat_app_url=chat_app_url,
            chat_app_username=os.getenv("JESSE_USERNAME"),
            chat_app_password=os.getenv("JESSE_PASSWORD")
        )
        if auth_token is None:
            print("Failed to get authentication token")
            return None
    
    url = f"{chat_app_url.rstrip('/')}/api/v1/users"
    
    headers = {
        "Authorization": auth_token
    }
    
    print(f"Retrieving all users")
    try:
        response = requests.get(url, headers=headers)
        print(f"Response status: {response.status_code}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Failed to retrieve users: {e}")
        return None

def print_users(auth_token=None, chat_app_url=None):
    """Print all users in a readable format with their online status."""
    users = get_all_users(auth_token, chat_app_url)
    if not users:
        print("No users found")
        return
    
    print("\nUsers:")
    print("-" * 50)
    
    # Sort users by online status (online first) then by username
    sorted_users = sorted(users, key=lambda x: (-x['online_status'], x['username'].lower()))
    
    for user in sorted_users:
        status = "🟢 Online" if user['online_status'] else "⚫ Offline"
        created_at = datetime.fromisoformat(user['created_at'].replace('Z', '+00:00'))
        formatted_time = created_at.strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"{user['username']} - {status}")
        print(f"Joined: {formatted_time}")
        print(f"Email: {user['email']}")
        print("-" * 50)

if __name__ == "__main__":
    # Example usage
    chat_app_url = os.getenv('chat_app_url')
    auth_token = login_user(
        chat_app_url=chat_app_url,
        chat_app_username=os.getenv("JESSE_USERNAME"),
        chat_app_password=os.getenv("JESSE_PASSWORD")
    )
    if auth_token:
        print("\nGetting all users:")
        print_users(auth_token)
        
        print("\nGetting all channels:")
        channels = get_all_channels(auth_token)
        if channels:
            print("\nAvailable channels:")
            for channel in channels:
                print(f"Channel: {channel.get('name', 'Unnamed')} (ID: {channel.get('id')})")
                print("Getting messages from this channel:")
                messages = get_channel_messages(channel['id'], auth_token)
                if messages:
                    print(f"Found {len(messages)} messages")
                    for msg in messages:
                        print(f"- {msg.get('username')}: {msg.get('content')}")
                print("-" * 50)
        
        print("\nGetting messages from user 'hank':")
        print_user_messages("hank", auth_token)