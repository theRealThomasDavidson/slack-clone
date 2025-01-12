import os
import logging
from uuid import uuid4

logger = logging.getLogger(__name__)

class Settings:
    APP_NAME: str = "Chat API"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database settings
    POSTGRES_USER: str = os.getenv("POSTGRES_USER", "postgres")
    POSTGRES_PASSWORD: str = os.getenv("POSTGRES_PASSWORD", "postgres")
    POSTGRES_DB: str = os.getenv("POSTGRES_DB", "postgres")
    POSTGRES_HOST: str = os.getenv("POSTGRES_HOST", "db")
    POSTGRES_PORT: int = int(os.getenv("POSTGRES_PORT", "5432"))
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # Redis settings
    REDIS_HOST: str = os.getenv("REDIS_HOST", "redis")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    
    # Server settings
    SERVER_ID: str = str(uuid4())
    WS_MESSAGE_QUEUE_SIZE: int = 1000
    MAX_MESSAGES: int = 100

    def log_config(self):
        """Log all configuration settings"""
        logger.info("=== Environment Configuration ===")
        for key, value in self.__dict__.items():
            if not key.startswith("_"):
                logger.info(f"{key}: {value}")
        logger.info(f"DATABASE_URL: {self.DATABASE_URL}")
        logger.info("===============================")

settings = Settings()
settings.log_config()  # Log all settings when initialized 