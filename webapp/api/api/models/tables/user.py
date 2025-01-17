"""SQLAlchemy User model."""

from sqlalchemy import Column, Integer, String, DateTime, Boolean
from sqlalchemy.orm import relationship
from datetime import datetime

from ...database import Base

class User(Base):
    """User table model."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    messages = relationship("Message", back_populates="user")
    channels = relationship("Channel", secondary="channel_members", back_populates="members")
    reactions = relationship("Reaction", back_populates="user")
    files = relationship("File", foreign_keys="[File.user_id]") 