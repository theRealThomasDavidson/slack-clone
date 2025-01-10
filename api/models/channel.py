from pydantic import BaseModel, Field, validator
from typing import Dict, List, Optional, Literal
from sqlalchemy import Column, String, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
import enum

class ChannelType(str, enum.Enum):
    PUBLIC = "public"
    PRIVATE = "private"

class MemberExceptionDB(Base):
    __tablename__ = "member_exceptions"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    channel_id: Mapped[str] = mapped_column(String, ForeignKey("channels.id", ondelete="CASCADE"), index=True)
    user_id: Mapped[str] = mapped_column(String, index=True)

class ChannelCreate(BaseModel):
    name: str = Field(..., min_length=1, max_length=50)
    description: str = Field(default="")
    type: ChannelType = Field(default=ChannelType.PUBLIC)

    @validator('name')
    def name_must_be_valid(cls, v):
        if not v.strip():
            raise ValueError('Channel name cannot be empty or just whitespace')
        if not v.replace('-', '').replace('_', '').isalnum():
            raise ValueError('Channel name can only contain letters, numbers, hyphens, and underscores')
        return v.lower()  # Normalize to lowercase

class Channel(ChannelCreate):
    id: str
    created_by: str
    members: List[str] = []
    member_exceptions: List[str] = []  # List of user IDs that are exceptions to the default behavior

class ChannelDB(Base):
    __tablename__ = "channels"
    __table_args__ = (
        UniqueConstraint('name', name='uq_channel_name'),
    )

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True)  # Added index for faster lookups
    description: Mapped[str] = mapped_column(String)
    created_by: Mapped[str] = mapped_column(String)
    members: Mapped[List[str]] = mapped_column(String)  # Stored as JSON
    type: Mapped[ChannelType] = mapped_column(String)
    member_exceptions: Mapped[List[MemberExceptionDB]] = relationship(
        "MemberExceptionDB",
        cascade="all, delete-orphan"
    )