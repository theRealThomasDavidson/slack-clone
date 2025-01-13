import requests
from src.utils.env import load_env_vars
from .auth import login_user

def get_all_channels(auth_token=None, chat_app_url=None):
    """
    Retrieve all available channels.
    If auth_token is not provided, will attempt to login using env credentials.
    """
    config = load_env_vars()
    if chat_app_url is None:
        chat_app_url = config['chat_app_url']
    
    # Get auth token if not provided
    if auth_token is None:
        auth_token = login_user(chat_app_url=chat_app_url)
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
    config = load_env_vars()
    if chat_app_url is None:
        chat_app_url = config['chat_app_url']
    
    # Get auth token if not provided
    if auth_token is None:
        auth_token = login_user(chat_app_url=chat_app_url)
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
    config = load_env_vars()
    if chat_app_url is None:
        chat_app_url = config['chat_app_url']
    
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

if __name__ == "__main__":
    # Example usage
    auth_token = login_user()
    if auth_token:
        # First get all channels
        print("\nGetting all channels:")
        channels = get_all_channels(auth_token)
        if channels:
            print("\nAvailable channels:")
            for channel in channels:
                print(f"- {channel.get('name', 'Unnamed')} (ID: {channel.get('id', 'No ID')})")
            
            # Find Saul's office channel
            sauls_office = next((channel for channel in channels if channel['name'] == 'sauls-office'), None)
            if sauls_office:
                print(f"\nGetting messages from Saul's office (ID: {sauls_office['id']}):")
                channel_messages = get_channel_messages(sauls_office['id'], auth_token)
                if channel_messages:
                    print("\nMessages and Replies:")
                    print_message_tree(channel_messages, auth_token, None)
            else:
                print("\nCouldn't find Saul's office channel") 