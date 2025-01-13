"""Authentication service."""

from datetime import datetime, timedelta
from typing import Dict, Optional
import jwt
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.user import UserCreate
from ..models.tables.user import User as UserTable
from ..core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# In-memory store for user activity
user_last_seen: Dict[str, datetime] = {}

class AuthService:
    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        """Verify password."""
        return pwd_context.verify(plain_password, hashed_password)

    @staticmethod
    def get_password_hash(password: str) -> str:
        """Get password hash."""
        return pwd_context.hash(password)

    @staticmethod
    def create_access_token(data: dict) -> str:
        """Create access token."""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
        return encoded_jwt

    @staticmethod
    def verify_token(token: str) -> Optional[str]:
        """Verify token."""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                return None
            return username
        except InvalidTokenError:
            return None

    @staticmethod
    async def get_user_by_email(db: AsyncSession, email: str) -> Optional[UserTable]:
        """Get user by email."""
        result = await db.execute(select(UserTable).filter(UserTable.email == email))
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_username(db: AsyncSession, username: str) -> Optional[UserTable]:
        """Get user by username."""
        result = await db.execute(select(UserTable).filter(UserTable.username == username))
        return result.scalar_one_or_none()

    @staticmethod
    async def authenticate_user(db: AsyncSession, username: str, password: str) -> Optional[UserTable]:
        """Authenticate user."""
        user = await AuthService.get_user_by_username(db, username)
        if not user:
            return None
        if not AuthService.verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    async def create_user(db: AsyncSession, user: UserCreate) -> UserTable:
        """Create user."""
        db_user = UserTable(
            email=user.email,
            username=user.username,
            hashed_password=AuthService.get_password_hash(user.password)
        )
        db.add(db_user)
        await db.commit()
        await db.refresh(db_user)
        return db_user 

    @staticmethod
    def update_user_activity(username: str) -> None:
        """Update the last seen timestamp for a user."""
        user_last_seen[username] = datetime.utcnow()
    
    @staticmethod
    def is_user_active(username: str) -> bool:
        """Check if a user has been active in the last 5 seconds."""
        if username not in user_last_seen:
            return False
        return datetime.utcnow() - user_last_seen[username] <= timedelta(seconds=5) 