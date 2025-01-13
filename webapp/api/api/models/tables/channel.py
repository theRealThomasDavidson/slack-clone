"""SQLAlchemy Channel model."""

from datetime import datetime
from sqlalchemy import Boolean, Column, DateTime, Integer, String, Table, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from ...database import Base

# Association table for channel members
channel_members = Table(
    'channel_members',
    Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id'), primary_key=True),
    Column('channel_id', Integer, ForeignKey('channels.id'), primary_key=True)
)

class Channel(Base):
    """Channel table model."""
    __tablename__ = "channels"
    __table_args__ = (
        UniqueConstraint('name', name='uq_channel_name'),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False, unique=True, index=True)
    description = Column(String)
    is_private = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships using string references
    members = relationship("User", secondary=channel_members, back_populates="channels")
    messages = relationship("Message", back_populates="channel") 