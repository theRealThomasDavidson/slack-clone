from typing import Optional, Dict
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from ..models.user import User, UserCreate
from ..models.auth import Token, TokenData
from ..repositories.user import UserRepository
from ..core.security import verify_password, get_password_hash, create_access_token, verify_token
from ..core.config import settings

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

class AuthService:
    _instance = None
    _active_tokens: Dict[str, datetime] = {}  # Shared across all instances

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        # Initialize only once
        if not hasattr(self, 'initialized'):
            self.initialized = True
            self.user_repository = UserRepository()

    async def authenticate_user(self, username: str, password: str) -> Optional[User]:
        user = self.user_repository.get_by_username(username)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    async def create_user(self, user_data: UserCreate) -> User:
        # Check if username exists
        if self.user_repository.get_by_username(user_data.username):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered"
            )
        
        # Create user with hashed password
        hashed_password = get_password_hash(user_data.password)
        return self.user_repository.create_user(user_data, hashed_password)

    async def login(self, username: str, password: str) -> Token:
        user = await self.authenticate_user(username, password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password",
                headers={"WWW-Authenticate": "Bearer"},
            )

        access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user.username}, expires_delta=access_token_expires
        )
        
        self._active_tokens[user.username] = datetime.utcnow() + access_token_expires
        return Token(access_token=access_token)

    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> User:
        print(f"Verifying token: {token[:20]}...")
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
        username = verify_token(token)
        print(f"Verified username: {username}")
        
        if username is None:
            print("Username was None")
            raise credentials_exception
            
        user = self.user_repository.get_by_username(username)
        print(f"Found user: {user}")
        
        if user is None:
            print("User was None")
            raise credentials_exception
            
        if username not in self._active_tokens:
            print(f"Username {username} not in active tokens")
            raise credentials_exception
            
        if datetime.utcnow() > self._active_tokens[username]:
            print(f"Token expired for {username}")
            raise credentials_exception
            
        return user

    async def logout(self, username: str):
        """Remove user's active token"""
        if username in self._active_tokens:
            del self._active_tokens[username] 