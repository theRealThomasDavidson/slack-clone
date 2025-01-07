from typing import List, Optional
from datetime import datetime
import uuid
from ..models.message import Message, MessageCreate
from .base import BaseRepository
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

class MessageRepository(BaseRepository[Message]):
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            super().__init__()
            self._initialized = True
            logger.info("Initialized MessageRepository singleton")

    def add_message(self, message: MessageCreate) -> Message:
        # Create a dict with all the required fields
        message_dict = message.model_dump()
        message_dict.update({
            'id': str(uuid.uuid4()),
            'timestamp': datetime.utcnow().isoformat()
        })
        
        # Create the message using the dict
        new_message = Message(**message_dict)
        self._items.append(new_message)
        
        # Keep only last N messages
        if len(self._items) > settings.MAX_MESSAGES:
            self._items.pop(0)
            
        logger.info(f"Added new message: {new_message}")
        logger.info(f"Total messages in repository: {len(self._items)}")
        return new_message

    def get_recent_messages(self) -> List[Message]:
        messages = self._items[-settings.MAX_MESSAGES:]
        logger.info(f"Retrieving {len(messages)} recent messages")
        return messages

    def get_user_messages(self, user_id: str) -> List[Message]:
        """Get all messages from a specific user"""
        messages = [msg for msg in self._items if msg.user_id == user_id]
        logger.info(f"Retrieved {len(messages)} messages for user {user_id}")
        return messages

    def clear_messages(self):
        """Clear all messages from the repository"""
        logger.info("Clearing all messages from repository")
        self._items = [] 