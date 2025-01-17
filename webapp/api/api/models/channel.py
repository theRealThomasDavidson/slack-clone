"""Channel models and schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

class ChannelBase(BaseModel):
    """Base channel model."""
    name: str = Field(..., min_length=1, max_length=50)
    description: Optional[str] = None
    is_private: bool = False

class ChannelCreate(ChannelBase):
    """Channel creation model."""
    pass

class Channel(ChannelBase):
    """Channel model with all fields."""
    id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""
        from_attributes = True 