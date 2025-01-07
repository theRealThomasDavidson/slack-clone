from typing import Optional, Dict, List
from datetime import datetime
import uuid
from ..models.user import User, UserCreate

class UserRepository:
    _instance = None
    _users: Dict[str, User] = {}
    _system_user_id = "00000000-0000-0000-0000-000000000000"

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Initialize only once
        if not hasattr(self, 'initialized'):
            self.initialized = True
            # Create system user if it doesn't exist
            if self._system_user_id not in self._users:
                self._users[self._system_user_id] = User(
                    id=self._system_user_id,
                    username="system",
                    email="system@chatapp.com",
                    display_name="System",
                    created_at=datetime.utcnow(),
                    is_online=True,
                    hashed_password="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewFpxQgKMQFD"  # Dummy hash
                )

    def create_user(self, user_data: UserCreate, hashed_password: str) -> User:
        """Create a new user"""
        user = User(
            id=str(uuid.uuid4()),
            username=user_data.username,
            email=user_data.email,
            display_name=user_data.display_name,
            created_at=datetime.utcnow(),
            is_online=True,
            hashed_password=hashed_password
        )
        self._users[user.id] = user
        return user

    def get_by_username(self, username: str) -> Optional[User]:
        """Get a user by username"""
        return next(
            (user for user in self._users.values() if user.username == username),
            None
        )

    def get_by_id(self, user_id: str) -> Optional[User]:
        """Get a user by ID"""
        return self._users.get(user_id)

    def get_all(self) -> List[User]:
        """Get all users"""
        return list(self._users.values())

    def update_user(self, user_id: str, update_data) -> Optional[User]:
        """Update user fields"""
        if user_id in self._users:
            user = self._users[user_id]
            update_dict = update_data.model_dump() if hasattr(update_data, 'model_dump') else update_data
            for key, value in update_dict.items():
                if hasattr(user, key):
                    setattr(user, key, value)
            return user
        return None

    def clear(self):
        """Clear all users (for testing)"""
        self._users = {}
    