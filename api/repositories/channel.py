from typing import List, Optional, Dict
from datetime import datetime
import uuid
from ..models.channel import Channel, ChannelCreate

class ChannelRepository:
    _instance = None
    _channels: Dict[str, Channel] = {}  # id -> Channel

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not hasattr(self, 'initialized'):
            self.initialized = True

    def create_channel(self, name: str, description: str, created_by: str) -> Channel:
        """Create a new channel"""
        channel = Channel(
            id=str(uuid.uuid4()),
            name=name,
            description=description,
            created_by=created_by,
            created_at=datetime.utcnow(),
            members=[created_by]  # Creator is automatically a member
        )
        self._channels[channel.id] = channel
        return channel

    def get_all(self) -> List[Channel]:
        """Get all channels"""
        return list(self._channels.values())

    def get_by_name(self, name: str) -> Optional[Channel]:
        """Get channel by name"""
        return next(
            (channel for channel in self._channels.values() if channel.name == name),
            None
        )

    def get_by_id(self, channel_id: str) -> Optional[Channel]:
        """Get channel by ID"""
        return self._channels.get(channel_id)

    def add_member(self, channel_id: str, user_id: str) -> Optional[Channel]:
        """Add a member to a channel"""
        channel = self._channels.get(channel_id)
        if not channel:
            return None
        if user_id not in channel.members:
            channel.members.append(user_id)
        return channel

    def remove_member(self, channel_id: str, user_id: str) -> Optional[Channel]:
        """Remove a member from a channel"""
        channel = self._channels.get(channel_id)
        if not channel or user_id not in channel.members:
            return None
        channel.members.remove(user_id)
        return channel

    def clear(self):
        """Clear all channels (for testing)"""
        self._channels.clear()

    def delete(self, channel_id: str) -> bool:
        """Delete a channel"""
        if channel_id in self._channels:
            del self._channels[channel_id]
            return True
        return False

    def get_user_channels(self, user_id: str) -> List[Channel]:
        """Get all channels a user is a member of"""
        return [
            channel for channel in self._channels.values()
            if user_id in channel.members
        ] 