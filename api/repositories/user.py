from typing import Optional, Dict, List
from datetime import datetime
import uuid
import bcrypt
from sqlalchemy.orm import Session
from sqlalchemy import select
from ..models.user import User, UserCreate, UserUpdate, UserDB

class UserRepository:
    _instance = None
    _initialized = False

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, db: Session):
        if not self._initialized:
            self.db = db
            self._initialized = True

    def create_user(self, user_data: UserCreate) -> User:
        """Create a new user"""
        # Check if username or email already exists
        if self.get_by_username(user_data.username):
            raise ValueError("Username already exists")
        if self.get_by_email(user_data.email):
            raise ValueError("Email already exists")
            
        # Hash password
        password_hash = bcrypt.hashpw(
            user_data.password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')
        
        # Create user
        db_user = UserDB(
            id=str(uuid.uuid4()),
            username=user_data.username,
            email=user_data.email,
            display_name=user_data.display_name,
            password_hash=password_hash,
            is_online=True,
            created_at=datetime.utcnow()
        )
        
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        
        return User.model_validate(db_user)

    def get_by_username(self, username: str) -> Optional[User]:
        """Get a user by username"""
        db_user = self.db.query(UserDB).filter(UserDB.username == username).first()
        return User.model_validate(db_user) if db_user else None

    def get_by_email(self, email: str) -> Optional[User]:
        """Get a user by email"""
        db_user = self.db.query(UserDB).filter(UserDB.email == email).first()
        return User.model_validate(db_user) if db_user else None

    def get_by_id(self, user_id: str) -> Optional[User]:
        """Get a user by ID"""
        db_user = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        return User.model_validate(db_user) if db_user else None

    def get_all_users(self) -> List[User]:
        """Get all users"""
        db_users = self.db.query(UserDB).all()
        return [User.model_validate(u) for u in db_users]

    def update_display_name(self, user_id: str, display_name: str) -> User:
        """Update a user's display name"""
        db_user = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        if not db_user:
            raise ValueError("User not found")
            
        db_user.display_name = display_name
        db_user.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_user)
        
        return User.model_validate(db_user)

    def set_online_status(self, user_id: str, is_online: bool) -> User:
        """Set a user's online status"""
        db_user = self.db.query(UserDB).filter(UserDB.id == user_id).first()
        if not db_user:
            raise ValueError("User not found")
            
        db_user.is_online = is_online
        db_user.updated_at = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(db_user)
        
        return User.model_validate(db_user)

    def verify_password(self, password: str, password_hash: str) -> bool:
        """Verify a password against its hash"""
        return bcrypt.checkpw(
            password.encode('utf-8'),
            password_hash.encode('utf-8')
        )
    