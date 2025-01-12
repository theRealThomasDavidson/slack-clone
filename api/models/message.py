from pydantic import BaseModel, Field, ConfigDict, field_validator
from datetime import datetime
from typing import Optional, Dict, Any, List
from sqlalchemy import Column, String, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func
from .base import Base

class MessageCreate(BaseModel):
    content: str = Field(..., max_length=1000)
    channel_id: str
    username: Optional[str] = None
    user_id: Optional[str] = None
    parent_id: Optional[str] = None

class MessageParentRecall(BaseModel):
    content: str = Field(..., max_length=1000)
    channel_id: str
    username: Optional[str] = None
    user_id: Optional[str] = None
class MessageRecall(BaseModel):
    content: str = Field(..., max_length=1000)
    channel_id: str
    username: Optional[str] = None
    user_id: Optional[str] = None
    parent: Optional[MessageParent] = None
class MessageDB(Base):
    __tablename__ = "messages"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    content: Mapped[str] = mapped_column(String(1000))
    channel_id: Mapped[str] = mapped_column(String, index=True)
    username: Mapped[str] = mapped_column(String)
    user_id: Mapped[str] = mapped_column(String)
    parent_id: Mapped[Optional[str]] = mapped_column(String, ForeignKey("messages.id"), nullable=True, index=True)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), 
        server_default=func.now()
    )

    # Relationships
    replies: Mapped[List["MessageDB"]] = relationship(
        "MessageDB",
        backref="parent_message",
        remote_side=[id],
        lazy="joined",
        cascade="all, delete-orphan"
    )

class Message(MessageCreate):
    id: str
    username: str  # Override optional
    user_id: str   # Override optional
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    replies_count: Optional[int] = Field(default=0)
    parent_message: Optional["Message"] = None

    model_config = ConfigDict(
        from_attributes=True,
        json_encoders={datetime: lambda dt: dt.isoformat()}
    )

    @field_validator('timestamp', mode='before')
    @classmethod
    def parse_timestamp(cls, value):
        if isinstance(value, str):
            try:
                return datetime.fromisoformat(value)
            except ValueError:
                try:
                    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S.%f")
                except ValueError:
                    return datetime.strptime(value, "%Y-%m-%dT%H:%M:%S")
        return value

    def model_dump(self, **kwargs) -> Dict[str, Any]:
        data = super().model_dump(**kwargs)
        if isinstance(self.timestamp, datetime):
            data['timestamp'] = self.timestamp.isoformat()
        return data

Message.model_rebuild()  # Update forward refs