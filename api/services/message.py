from ..models.message import Message, MessageCreate
from ..repositories.message import MessageRepository
from ..utils.websocket import ConnectionManager
from typing import List

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
            self.repository = MessageRepository()
            self._initialized = True
    
    async def add_message(self, message: MessageCreate) -> Message:
        # Only check connection for websocket messages (when channel_id is "global")
        if message.channel_id == "global" and not self.connection_manager.is_connected(message.username):
            raise ValueError("User is not connected")
            
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
    
    def get_channel_messages(self, channel_id: str) -> List[Message]:
        """Get all messages in a specific channel"""
        return [msg for msg in self.get_recent_messages() if msg.channel_id == channel_id]

    def clear_messages(self):
        """Clear all messages from the repository"""
        self.repository.clear_messages() 