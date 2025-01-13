"""SQLAlchemy Reaction model."""

from datetime import datetime
from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship

from ...database import Base

class Reaction(Base):
    """Reaction table model."""
    __tablename__ = "reactions"

    id = Column(Integer, primary_key=True, index=True)
    emoji = Column(String, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    message_id = Column(Integer, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Relationships
    user = relationship("User", back_populates="reactions")
    message = relationship("Message", back_populates="reactions")

    # Add unique constraint for user_id, message_id, and emoji combination
    __table_args__ = (
        UniqueConstraint('user_id', 'message_id', 'emoji', name='unique_user_message_emoji'),
    ) 