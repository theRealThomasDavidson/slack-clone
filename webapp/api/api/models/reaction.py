from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class ReactionBase(BaseModel):
    """Base reaction model."""
    emoji: str
    message_id: int

class ReactionCreate(ReactionBase):
    """Reaction creation model."""
    pass

class Reaction(ReactionBase):
    """Reaction response model."""
    id: int
    user_id: int
    username: str
    created_at: datetime

    class Config:
        """Pydantic config."""
        from_attributes = True
        json_schema_extra = {
            "example": {
                "emoji": "👍",
                "message_id": 1,
                "id": 1,
                "user_id": 1,
                "username": "peggyolson",
                "created_at": "2025-01-09T23:34:13.812739"
            }
        } 