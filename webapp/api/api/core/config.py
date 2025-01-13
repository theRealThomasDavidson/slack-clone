"""Configuration settings for the application."""

from typing import Optional, List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Application settings
    APP_NAME: str = "Chat API"
    API_V1_STR: str = "/api/v1"
    DEBUG: bool = True

    # Authentication
    SECRET_KEY: str = "your-secret-key-here"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@db:5432/chat_db"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: str = "5432"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "chat_db"

    # Redis
    REDIS_HOST: str = "redis"
    REDIS_PORT: str = "6379"

    # CORS
    BACKEND_CORS_ORIGINS: List[str] = ["*"]

    # File Upload
    MAX_UPLOAD_SIZE: int = 10 * 1024 * 1024  # 10MB
    UPLOAD_DIR: str = "uploads"

    # Rate Limiting
    RATE_LIMIT_PER_USER: int = 100
    RATE_LIMIT_WINDOW_SECONDS: int = 60

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"  # Allow extra fields from env file

settings = Settings() 