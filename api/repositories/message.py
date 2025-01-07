from typing import List, Optional
from datetime import datetime
import uuid
from ..models.message import Message, MessageCreate
from .base import BaseRepository
from ..core.config import settings

class MessageRepository(BaseRepository[Message]):
    def add_message(self, message: MessageCreate) -> Message:
        # Create a dict with all the required fields
        message_dict = message.model_dump()
        message_dict.update({
            'id': str(uuid.uuid4()),
            'timestamp': datetime.utcnow()
        })
        
        # Create the message using the dict
        new_message = Message(**message_dict)
        self._items.append(new_message)
        
        # Keep only last N messages
        if len(self._items) > settings.MAX_MESSAGES:
            self._items.pop(0)
            
        return new_message

    def get_recent_messages(self) -> List[Message]:
        return self._items[-settings.MAX_MESSAGES:]

    def get_user_messages(self, user_id: str) -> List[Message]:
        """Get all messages from a specific user"""
        return [msg for msg in self._items if msg.user_id == user_id]

    def clear_messages(self):
        """Clear all messages from the repository"""
        self._items = [] 