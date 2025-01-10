from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional
from sqlalchemy import Column, String, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class FileDB(Base):
    __tablename__ = "files"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    filename: Mapped[str] = mapped_column(String)
    size: Mapped[int] = mapped_column(Integer)
    content_type: Mapped[str] = mapped_column(String)
    storage_path: Mapped[str] = mapped_column(String)
    uploaded_by: Mapped[str] = mapped_column(String, ForeignKey("users.id", ondelete="CASCADE"))
    channel_id: Mapped[str] = mapped_column(String, ForeignKey("channels.id", ondelete="CASCADE"))
    message_id: Mapped[str] = mapped_column(String, ForeignKey("messages.id", ondelete="CASCADE"))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default="now()")

class FileCreate(BaseModel):
    filename: str = Field(..., min_length=1, max_length=255)
    size: int = Field(..., gt=0)
    content_type: str
    channel_id: str

class File(BaseModel):
    id: str
    filename: str
    size: int
    content_type: str
    storage_path: str
    uploaded_by: str
    channel_id: str
    message_id: str
    created_at: datetime

    class Config:
        from_attributes = True 