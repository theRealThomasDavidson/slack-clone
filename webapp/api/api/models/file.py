from pydantic import BaseModel
from datetime import datetime
from uuid import UUID

class FileBase(BaseModel):
    """Base file model."""
    filename: str
    filepath: str
    content_type: str
    size: int
    user_id: int

class FileCreate(FileBase):
    """File creation model."""
    pass

class File(FileBase):
    """File response model."""
    id: UUID
    created_at: datetime

    class Config:
        """Pydantic config."""
        from_attributes = True 