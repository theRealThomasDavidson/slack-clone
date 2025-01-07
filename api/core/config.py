from pydantic_settings import BaseSettings
from datetime import timedelta
from pydantic import ConfigDict

class Settings(BaseSettings):
    APP_NAME: str = "Chat API"
    DEBUG: bool = True
    SECRET_KEY: str = "your-secret-key-here"  # Change in production
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    MAX_MESSAGES: int = 50
    MAX_MESSAGE_LENGTH: int = 1000
    RATE_LIMIT_MESSAGES: int = 3
    RATE_LIMIT_SECONDS: int = 5

    model_config = ConfigDict(env_file=".env")

settings = Settings() 