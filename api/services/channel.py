from typing import List, Optional
from ..models.channel import Channel, ChannelCreate, ChannelType
from ..repositories.channel import ChannelRepository
from ..utils.websocket import ConnectionManager
from fastapi import HTTPException, status
from ..core.database import SessionLocal

class ChannelService:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            db = SessionLocal()
            self.repository = ChannelRepository(db)
            self.connection_manager = ConnectionManager()
            self._initialized = True

    def create_channel(self, name: str, description: str, created_by: str, channel_type: ChannelType = ChannelType.PUBLIC) -> Channel:
        """Create a new channel"""
        try:
            return self.repository.create_channel(name, description, created_by, channel_type)
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def get_channel(self, channel_id: str) -> Optional[Channel]:
        """Get a channel by ID"""
        channel = self.repository.get_by_id(channel_id)
        if not channel:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
        return channel

    def get_all_channels(self) -> List[Channel]:
        """Get all channels"""
        return self.repository.get_all()

    def add_member(self, channel_id: str, user_id: str) -> Channel:
        """Add a member to a channel"""
        try:
            channel = self.repository.add_member(channel_id, user_id)
            if not channel:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
            return channel
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def remove_member(self, channel_id: str, user_id: str) -> Channel:
        """Remove a member from a channel"""
        channel = self.repository.remove_member(channel_id, user_id)
        if not channel:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
        return channel

    def set_member_exception(self, channel_id: str, user_id: str) -> Channel:
        """Set a member exception (ban from public channel or allow in private channel)"""
        try:
            channel = self.repository.set_member_exception(channel_id, user_id)
            if not channel:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
            return channel
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def remove_member_exception(self, channel_id: str, user_id: str) -> Channel:
        """Remove a member exception"""
        try:
            channel = self.repository.remove_member_exception(channel_id, user_id)
            if not channel:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Channel not found")
            return channel
        except ValueError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))

    def get_user_channels(self, user_id: str) -> List[Channel]:
        """Get all channels a user is a member of"""
        return self.repository.get_user_channels(user_id)

    def delete_channel(self, channel_id: str) -> bool:
        """Delete a channel"""
        return self.repository.delete(channel_id) 