from pydantic import BaseModel, Field, EmailStr, ConfigDict
from typing import Optional
from datetime import datetime

class UserBase(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr
    display_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=8)

class User(UserBase):
    id: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    is_online: bool = False
    last_seen: Optional[datetime] = None
    hashed_password: str

class UserResponse(UserBase):
    id: str
    created_at: datetime
    is_online: bool
    last_seen: Optional[datetime] = None

    model_config = ConfigDict(from_attributes=True)

class UserUpdate(BaseModel):
    display_name: Optional[str] = None
    email: Optional[EmailStr] = None