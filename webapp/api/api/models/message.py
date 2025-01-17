from pydantic import BaseModel
from fastapi import UploadFile
from datetime import datetime
from typing import Optional, List, Dict
from uuid import UUID

class FileInfo(BaseModel):
    """File information model."""
    id: str  # Changed from UUID to str since we're passing string representation
    filename: str
    size: int
    content_type: str

    class Config:
        """Pydantic config."""
        from_attributes = True
        orm_mode = True  # Enable ORM mode for SQLAlchemy compatibility

class MessageBase(BaseModel):
    """Base message model."""
    content: str
    channel_id: int
    user_id: Optional[int] = None
    parent_id: Optional[int] = None  # For thread support

class MessageCreate(MessageBase):
    """Message creation model."""
    pass  # Removed file field as it's handled by FastAPI Form

class Message(MessageBase):
    """Message response model."""
    id: int
    created_at: datetime
    updated_at: datetime
    user_id: int  # Override to make required in response
    username: str
    emojis: Dict[str, List[str]] = {}  # {emoji: [usernames]}
    file: Optional[FileInfo] = None  # File information if this is a file message
    
    # Thread-related fields
    parent_message: Optional["Message"] = None
    replies: List["Message"] = []
    replies_count: int = 0

    class Config:
        """Pydantic config."""
        from_attributes = True
        orm_mode = True  # Enable ORM mode 

Message.model_rebuild()  # Update forward refs 