"""SQLAlchemy Message model."""

from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship

from ...database import Base

class Message(Base):
    """Message table model."""
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    content = Column(Text, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    channel_id = Column(Integer, ForeignKey("channels.id"), nullable=False)
    parent_id = Column(Integer, ForeignKey("messages.id"), nullable=True, index=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="messages")
    channel = relationship("Channel", back_populates="messages")
    reactions = relationship("Reaction", back_populates="message")
    file = relationship("File", back_populates="message", uselist=False)
    
    # Thread relationships
    parent_message = relationship("Message", remote_side=[id], back_populates="replies")
    replies = relationship("Message", back_populates="parent_message", cascade="all, delete-orphan") 