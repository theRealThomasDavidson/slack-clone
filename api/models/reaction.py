from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from sqlalchemy import Column, String, DateTime, ForeignKey
from ..core.database import Base

class ReactionDB(Base):
    __tablename__ = "reactions"

    id = Column(String, primary_key=True, index=True)
    message_id = Column(String, ForeignKey("messages.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    emoji = Column(String(32), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class ReactionBase(BaseModel):
    message_id: str
    emoji: str = Field(..., max_length=32)

class ReactionCreate(ReactionBase):
    pass

class Reaction(ReactionBase):
    id: str
    user_id: str
    created_at: datetime

    class Config:
        from_attributes = True 