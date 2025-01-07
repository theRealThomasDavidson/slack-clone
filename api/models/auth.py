from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime

class TokenData(BaseModel):
    username: str
    exp: datetime

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class LoginRequest(BaseModel):
    username: str
    password: str

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=30)
    email: EmailStr
    password: str = Field(..., min_length=8)
    display_name: Optional[str] = None 