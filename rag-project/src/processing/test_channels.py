"""
Test script to check channel access for Jesse's account.
"""
from src.client.auth import login_user
from src.utils.env import load_env_vars
import requests

def test_channels():
    # Load config
    config = load_env_vars()
    
    # Login as Jesse
    response = login_user(
        chat_app_url=config["chat_app_url"],
        chat_app_username="pinkman",
        chat_app_password="sciencebitch"
    )
    
    if response is None:
        print("Login failed yo! Response is None")
        return
        
    token = response
    print("Logged in successfully!")
    
    base_url = config["chat_app_url"].rstrip('/')
    headers = {"Authorization": token}
    
    # Get public channels
    channels_url = f"{base_url}/api/v1/channels"
    response = requests.get(channels_url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to get public channels! Status: {response.status_code}")
        print(response.text)
        return
        
    channels = response.json()
    print("\nPublic channels:")
    for channel in channels:
        print(f"- {channel['name']} (ID: {channel['id']}, Private: {channel.get('is_private', False)})")

    # Get my channels including DMs
    my_channels_url = f"{base_url}/api/v1/channels/me"
    response = requests.get(my_channels_url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to get my channels! Status: {response.status_code}")
        print(response.text)
        return
        
    my_channels = response.json()
    print("\nMy channels (including DMs):")
    for channel in my_channels:
        print(f"- {channel['name']} (ID: {channel['id']}, Private: {channel.get('is_private', False)})")
        # Print full channel data to inspect DM-specific fields
        print(f"  Full data: {channel}")

if __name__ == "__main__":
    test_channels() 