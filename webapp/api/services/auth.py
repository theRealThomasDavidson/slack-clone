from datetime import datetime, timedelta
from typing import Optional
import jwt
from fastapi import HTTPException, status
from ..models.user import User, UserCreate
from ..repositories.user import UserRepository
from ..utils.websocket import ConnectionManager
from .channel import ChannelService
from ..core.config import settings
from ..core.database import SessionLocal

class AuthService:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            db = SessionLocal()
            self.repository = UserRepository(db)
            self.channel_service = ChannelService()
            self.connection_manager = ConnectionManager()
            self._initialized = True

    def create_access_token(self, user: User) -> str:
        """Create a new access token for a user"""
        expiration = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        
        token_data = {
            "sub": user.id,
            "username": user.username,
            "exp": expiration
        }
        
        return jwt.encode(token_data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

    def verify_token(self, token: str) -> Optional[User]:
        """Verify an access token and return the user if valid"""
        try:
            payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
            user_id = payload.get("sub")
            if user_id is None:
                return None
            return self.repository.get_by_id(user_id)
        except jwt.PyJWTError:
            return None

    def register(self, user_data: UserCreate) -> User:
        """Register a new user"""
        try:
            return self.repository.create_user(user_data)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            )

    def login(self, username: str, password: str) -> tuple[User, str]:
        """Login a user and return their access token"""
        user = self.repository.get_by_username(username)
        if not user or not self.repository.verify_password(password, user.password_hash):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )
            
        # Update online status
        user = self.repository.set_online_status(user.id, True)
        
        # Generate access token
        access_token = self.create_access_token(user)
        
        return user, access_token

    def logout(self, user_id: str):
        """Logout a user"""
        self.repository.set_online_status(user_id, False)

    def get_user_by_id(self, user_id: str) -> Optional[User]:
        """Get a user by their ID"""
        return self.repository.get_by_id(user_id)

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get a user by their username"""
        return self.repository.get_by_username(username)

    def get_all_users(self) -> list[User]:
        """Get all users"""
        return self.repository.get_all_users()

    def update_display_name(self, user_id: str, display_name: str) -> User:
        """Update a user's display name"""
        try:
            return self.repository.update_display_name(user_id, display_name)
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=str(e)
            ) 