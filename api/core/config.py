import os
import secrets
from pydantic_settings import BaseSettings
import uuid

class Settings(BaseSettings):
    APP_NAME: str = "Chat API"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days
    ALGORITHM: str = "HS256"  # JWT encoding algorithm
    
    # Redis settings
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    SERVER_ID: str = str(uuid.uuid4())  # Unique ID for this server instance
    
    # WebSocket settings
    WS_MESSAGE_QUEUE_SIZE: int = 1000
    MAX_MESSAGES: int = 100  # Maximum number of messages to keep per channel
    
    class Config:
        env_file = ".env"

settings = Settings() 