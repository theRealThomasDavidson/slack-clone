"""
Track and fetch new messages from the chat app.
Stores last checked timestamp and only processes new messages.
"""
import os
import json
from datetime import datetime
import requests
from dotenv import load_dotenv
from ..client.auth import login_user

class MessageTracker:
    def __init__(self):
        load_dotenv()
        self.base_url = os.getenv("chat_app_url").rstrip('/')
        self.auth_token = None
        self.tracker_file = "last_checked.json"
        self.login()
        
    def login(self):
        """Login to the chat app."""
        self.auth_token = login_user(
            chat_app_url=os.getenv("chat_app_url"),
            chat_app_username="pinkman",
            chat_app_password="sciencebitch"
        )
        
    def get_last_checked(self):
        """Get the timestamp of last message check."""
        if not os.path.exists(self.tracker_file):
            return None
            
        with open(self.tracker_file, 'r') as f:
            data = json.load(f)
            return datetime.fromisoformat(data.get('last_checked'))
            
    def save_last_checked(self, timestamp=None):
        """Save timestamp as last checked."""
        if timestamp is None:
            timestamp = datetime.now().isoformat()
            
        with open(self.tracker_file, 'w') as f:
            json.dump({
                'last_checked': timestamp
            }, f)
            
    def get_new_messages(self):
        """Get messages newer than last check."""
        if not self.auth_token:
            print("Not logged in")
            return []
            
        headers = {"Authorization": self.auth_token}
        
        # Get all channels
        channels_url = f"{self.base_url}/api/v1/channels/me"
        response = requests.get(channels_url, headers=headers)
        
        if response.status_code != 200:
            print(f"Failed to get channels: {response.status_code}")
            return []
            
        channels = response.json()
        last_checked = self.get_last_checked()
        new_messages = []
        
        for channel in channels:
            # Get messages from channel
            messages_url = f"{self.base_url}/api/v1/messages/channel/{channel['id']}"
            response = requests.get(messages_url, headers=headers)
            
            if response.status_code != 200:
                print(f"Failed to get messages for channel {channel['name']}: {response.status_code}")
                continue
                
            messages = response.json()
            
            # Filter for new messages
            for msg in messages:
                msg_time = datetime.fromisoformat(msg['created_at'])
                if last_checked is None or msg_time > last_checked:
                    msg['channel_name'] = channel['name']
                    new_messages.append(msg)
        return new_messages
        
def main():
    """Run message tracking process."""
    tracker = MessageTracker()
    new_messages = tracker.get_new_messages()
    
    print(f"\nFound {len(new_messages)} new messages:")
    for msg in new_messages:
        print(f"Channel: {msg['channel_name']}")
        print(f"From: {msg['username']}")
        print(f"Message: {msg['content']}")
        print("---")
        
    # Update last_checked to latest message time, or current time if no messages
    if new_messages:
        tracker.save_last_checked(max(msg['created_at'] for msg in new_messages))
    
if __name__ == "__main__":
    main() 