import os
import secrets
from pydantic_settings import BaseSettings
import uuid
from pydantic import ConfigDict
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    APP_NAME: str = "Chat API"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 30  # 30 days
    ALGORITHM: str = "HS256"  # JWT encoding algorithm
    
    # Database settings
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "chat_db")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "localhost")
    POSTGRES_PORT: str = os.getenv("POSTGRES_PORT", "5432")
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Redis settings
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    SERVER_ID: str = str(uuid.uuid4())  # Unique ID for this server instance
    
    # WebSocket settings
    WS_MESSAGE_QUEUE_SIZE: int = 1000
    MAX_MESSAGES: int = 100  # Maximum number of messages to keep per channel
    
    model_config = ConfigDict(
        env_file = ".env",
        extra = "allow"  # Allow extra attributes
    )

    def log_config(self):
        """Log all configuration values"""
        logger.info("=== Environment Configuration ===")
        logger.info(f"APP_NAME: {self.APP_NAME}")
        logger.info(f"ALGORITHM: {self.ALGORITHM}")
        logger.info(f"ACCESS_TOKEN_EXPIRE_MINUTES: {self.ACCESS_TOKEN_EXPIRE_MINUTES}")
        logger.info(f"POSTGRES_USER: {self.POSTGRES_USER}")
        logger.info(f"POSTGRES_DB: {self.POSTGRES_DB}")
        logger.info(f"POSTGRES_HOST: {self.POSTGRES_HOST}")
        logger.info(f"POSTGRES_PORT: {self.POSTGRES_PORT}")
        logger.info(f"DATABASE_URL: {self.DATABASE_URL}")
        logger.info(f"REDIS_HOST: {self.REDIS_HOST}")
        logger.info(f"REDIS_PORT: {self.REDIS_PORT}")
        logger.info(f"SERVER_ID: {self.SERVER_ID}")
        logger.info(f"WS_MESSAGE_QUEUE_SIZE: {self.WS_MESSAGE_QUEUE_SIZE}")
        logger.info(f"MAX_MESSAGES: {self.MAX_MESSAGES}")
        logger.info("===============================")

settings = Settings()
settings.log_config()  # Log all settings when initialized 