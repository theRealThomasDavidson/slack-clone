"""User models and schemas."""

from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator
import re

EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z.]+$')

class UserBase(BaseModel):
    """Base user model."""
    username: str = Field(..., min_length=3, max_length=50)
    email: str

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: str) -> str:
        if not EMAIL_PATTERN.match(v):
            raise ValueError('Invalid email format')
        return v

class UserCreate(UserBase):
    """User creation model."""
    password: str = Field(..., min_length=8)

class UserUpdate(BaseModel):
    """User update model."""
    email: Optional[str] = None
    username: Optional[str] = Field(None, min_length=3, max_length=50)
    password: Optional[str] = Field(None, min_length=8)

    @field_validator('email')
    @classmethod
    def validate_email(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return v
        if not EMAIL_PATTERN.match(v):
            raise ValueError('Invalid email format')
        return v

class User(UserBase):
    """User response model."""
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config."""
        from_attributes = True 