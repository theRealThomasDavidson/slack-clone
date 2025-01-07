from typing import List, Optional, Dict
from datetime import datetime
import uuid
from ..models.user import User, UserCreate, UserUpdate
from .base import BaseRepository

class UserRepository:
    _instance = None
    _users = {}  # Shared storage across all instances

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Initialize only once
        if not hasattr(self, 'initialized'):
            self.initialized = True

    def create_user(self, user_data: UserCreate, hashed_password: str) -> User:
        user = User(
            id=str(uuid.uuid4()),
            username=user_data.username,
            email=user_data.email,
            display_name=user_data.display_name,
            hashed_password=hashed_password,
            created_at=datetime.utcnow(),
            is_online=True
        )
        self._users[user.username] = user
        return user

    def get_by_username(self, username: str) -> Optional[User]:
        return self._users.get(username)

    def clear(self):
        """Clear all users (for testing)"""
        self._users.clear()

    def get_all(self) -> List[User]:
        """Get all users"""
        return list(self._users.values())

    def update_user(self, user_id: str, update_data: UserUpdate) -> Optional[User]:
        """Update user data"""
        # Find user by id
        user = next((user for user in self._users.values() if user.id == user_id), None)
        if not user:
            return None
        
        # Update fields
        if update_data.display_name is not None:
            user.display_name = update_data.display_name
        if update_data.email is not None:
            user.email = update_data.email
        
        return user
    