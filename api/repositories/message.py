from typing import List, Optional
from datetime import datetime, timezone
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..models.message import Message, MessageCreate, MessageDB
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

class MessageRepository:
    def __init__(self, db: Session):
        self.db = db

    def add_message(self, message: MessageCreate) -> Message:
        # Create a dict with all the required fields
        message_dict = message.model_dump()
        message_dict.update({
            'id': str(uuid.uuid4()),
            'timestamp': datetime.now(timezone.utc)
        })
        
        # Create the database model
        db_message = MessageDB(**message_dict)
        self.db.add(db_message)
        self.db.commit()
        self.db.refresh(db_message)
        
        logger.info(f"Added new message: {db_message.id}")
        return Message.model_validate(db_message)

    def get_recent_messages(self, limit: int = None) -> List[Message]:
        """Get recent messages, optionally limited to a number"""
        if limit is None:
            limit = settings.MAX_MESSAGES

        messages = (
            self.db.query(MessageDB)
            .order_by(desc(MessageDB.timestamp))
            .limit(limit)
            .all()
        )
        logger.info(f"Retrieving {len(messages)} recent messages")
        return [Message.model_validate(msg) for msg in messages]

    def get_channel_messages(self, channel_id: str, limit: int = None) -> List[Message]:
        """Get messages for a specific channel"""
        if limit is None:
            limit = settings.MAX_MESSAGES

        messages = (
            self.db.query(MessageDB)
            .filter(MessageDB.channel_id == channel_id)
            .order_by(desc(MessageDB.timestamp))
            .limit(limit)
            .all()
        )
        return [Message.model_validate(msg) for msg in messages]

    def get_user_messages(self, user_id: str, limit: int = None) -> List[Message]:
        """Get messages from a specific user"""
        if limit is None:
            limit = settings.MAX_MESSAGES

        messages = (
            self.db.query(MessageDB)
            .filter(MessageDB.user_id == user_id)
            .order_by(desc(MessageDB.timestamp))
            .limit(limit)
            .all()
        )
        return [Message.model_validate(msg) for msg in messages]

    def clear_messages(self):
        """Clear all messages - used for testing"""
        self.db.query(MessageDB).delete()
        self.db.commit()
        logger.info("Cleared all messages") 