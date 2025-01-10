from typing import List, Optional, Dict
from datetime import datetime
import uuid
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..models.channel import Channel, ChannelCreate, ChannelType, ChannelDB, MemberExceptionDB

class ChannelRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_channel(
        self,
        name: str,
        description: str,
        created_by: str,
        channel_type: ChannelType = ChannelType.PUBLIC,
    ) -> Channel:
        """Create a new channel"""
        if self.get_by_name(name):
            raise ValueError("Channel name already exists")
            
        channel_dict = {
            "id": str(uuid.uuid4()),
            "name": name,
            "description": description,
            "created_by": created_by,
            "members": [created_by],  # Creator is automatically a member
            "type": channel_type
        }
        
        db_channel = ChannelDB(**channel_dict)
        self.db.add(db_channel)
        self.db.commit()
        self.db.refresh(db_channel)
        
        return Channel.model_validate(db_channel)

    def get_by_id(self, channel_id: str) -> Optional[Channel]:
        """Get channel by ID"""
        db_channel = self.db.query(ChannelDB).filter(ChannelDB.id == channel_id).first()
        return Channel.model_validate(db_channel) if db_channel else None

    def get_by_name(self, name: str) -> Optional[Channel]:
        """Get channel by name"""
        db_channel = self.db.query(ChannelDB).filter(ChannelDB.name == name).first()
        return Channel.model_validate(db_channel) if db_channel else None

    def get_all(self) -> List[Channel]:
        """Get all channels"""
        db_channels = self.db.query(ChannelDB).all()
        return [Channel.model_validate(ch) for ch in db_channels]

    def add_member(self, channel_id: str, user_id: str) -> Optional[Channel]:
        """Add a member to a channel"""
        db_channel = self.db.query(ChannelDB).filter(ChannelDB.id == channel_id).first()
        if not db_channel:
            return None
            
        # Check if user is in member_exceptions (banned)
        is_banned = self.db.query(MemberExceptionDB).filter(
            MemberExceptionDB.channel_id == channel_id,
            MemberExceptionDB.user_id == user_id
        ).first() is not None
        
        if is_banned:
            raise ValueError("User is banned from this channel")
            
        if user_id not in db_channel.members:
            db_channel.members.append(user_id)
            self.db.commit()
            self.db.refresh(db_channel)
            
        return Channel.model_validate(db_channel)

    def set_member_exception(self, channel_id: str, user_id: str) -> Optional[Channel]:
        """Add a member exception (ban from public channel or allow in private channel)"""
        db_channel = self.db.query(ChannelDB).filter(ChannelDB.id == channel_id).first()
        if not db_channel:
            return None
            
        # Cannot set exception for channel creator
        if user_id == db_channel.created_by:
            raise ValueError("Cannot modify channel creator's status")
            
        # Check if exception already exists
        existing_exception = self.db.query(MemberExceptionDB).filter(
            MemberExceptionDB.channel_id == channel_id,
            MemberExceptionDB.user_id == user_id
        ).first()
        
        if not existing_exception:
            exception = MemberExceptionDB(
                id=str(uuid.uuid4()),
                channel_id=channel_id,
                user_id=user_id
            )
            self.db.add(exception)
            
            # Remove from members if banned
            if user_id in db_channel.members:
                db_channel.members.remove(user_id)
                
            self.db.commit()
            
        return Channel.model_validate(db_channel)

    def remove_member_exception(self, channel_id: str, user_id: str) -> Optional[Channel]:
        """Remove a member exception"""
        db_channel = self.db.query(ChannelDB).filter(ChannelDB.id == channel_id).first()
        if not db_channel:
            return None
            
        # Cannot remove creator's exception
        if user_id == db_channel.created_by:
            raise ValueError("Cannot modify channel creator's status")
            
        self.db.query(MemberExceptionDB).filter(
            MemberExceptionDB.channel_id == channel_id,
            MemberExceptionDB.user_id == user_id
        ).delete()
        
        self.db.commit()
        return Channel.model_validate(db_channel)

    def remove_member(self, channel_id: str, user_id: str) -> Optional[Channel]:
        """Remove a member from a channel"""
        db_channel = self.db.query(ChannelDB).filter(ChannelDB.id == channel_id).first()
        if not db_channel or user_id not in db_channel.members:
            return None
            
        db_channel.members.remove(user_id)
        self.db.commit()
        self.db.refresh(db_channel)
        
        return Channel.model_validate(db_channel)

    def clear(self):
        """Clear all channels (for testing)"""
        self.db.query(ChannelDB).delete()
        self.db.commit()

    def delete(self, channel_id: str) -> bool:
        """Delete a channel"""
        result = self.db.query(ChannelDB).filter(ChannelDB.id == channel_id).delete()
        self.db.commit()
        return result > 0

    def get_user_channels(self, user_id: str) -> List[Channel]:
        """Get all channels a user is a member of"""
        db_channels = self.db.query(ChannelDB).filter(
            ChannelDB.members.contains([user_id])
        ).all()
        return [Channel.model_validate(ch) for ch in db_channels] 