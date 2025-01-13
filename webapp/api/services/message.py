from ..models.message import Message, MessageCreate
from ..repositories.message import MessageRepository
from ..utils.websocket import ConnectionManager
from ..repositories.channel import ChannelRepository
from typing import List
from fastapi import HTTPException, status
from ..core.database import SessionLocal

class MessageService:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.connection_manager = ConnectionManager()
            db = SessionLocal()
            self.repository = MessageRepository(db)
            self.channel_repository = ChannelRepository(db)
            self._initialized = True
    
    async def add_message(self, message: MessageCreate) -> Message:
        # Only check connection for websocket messages (when channel_id is "global")
        if message.channel_id == "global" and not self.connection_manager.is_connected(message.username):
            raise ValueError("User is not connected")
            
        # Check if user is banned from the channel
        if message.channel_id != "global":
            channel = self.channel_repository.get_by_id(message.channel_id)
            if not channel:
                raise ValueError("Channel not found")
            
            # Check if user is banned using member_exceptions
            is_banned = any(
                exc.user_id == message.user_id
                for exc in channel.member_exceptions
            )
            if is_banned:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="You cannot send messages to this channel"
                )
            
        # Create the message
        saved_message = self.repository.add_message(message)
        
        # Broadcast to channel subscribers if it's a channel message
        if message.channel_id != "global":
            await self.connection_manager.broadcast_to_channel(
                saved_message.model_dump(),
                message.channel_id
            )
        else:
            # Broadcast globally for global messages
            await self.connection_manager.broadcast(saved_message.model_dump())
            
        return saved_message
    
    def get_recent_messages(self) -> List[Message]:
        return self.repository.get_recent_messages()
    
    def get_user_messages(self, user_id: str) -> List[Message]:
        """Get all messages from a specific user"""
        return self.repository.get_user_messages(user_id)
    
    def get_channel_messages(self, channel_id: str, user_id: str) -> List[Message]:
        """Get all messages in a specific channel"""
        channel = self.channel_repository.get_by_id(channel_id)
        if not channel:
            raise ValueError("Channel not found")
            
        # Check if user is banned using member_exceptions
        is_banned = any(
            exc.user_id == user_id
            for exc in channel.member_exceptions
        )
        if is_banned:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You cannot view messages in this channel"
            )
            
        return self.repository.get_channel_messages(channel_id)

    def clear_messages(self):
        """Clear all messages from the repository"""
        self.repository.clear_messages() 