# Core Module Documentation

The core module provides fundamental functionality and configurations for the application.

## Configuration (`config.py`)

Handles application configuration using environment variables.

```python
class Settings(BaseSettings):
    APP_NAME: str = "Chat API"
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30

    class Config:
        env_file = ".env"
```

### Usage Example:
```python
from core.config import settings

# Access configuration
database_url = settings.DATABASE_URL
jwt_secret = settings.SECRET_KEY
```

## Database (`database.py`)

Manages database connections and session handling.

```python
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

# Create engine
engine = create_async_engine(settings.DATABASE_URL)

# Session factory
SessionLocal = sessionmaker(engine, class_=AsyncSession)

async def get_db() -> AsyncSession:
    """Dependency for getting DB sessions"""
    async with SessionLocal() as session:
        yield session
```

### Usage Example:
```python
from fastapi import Depends
from core.database import get_db

@app.get("/items")
async def get_items(db: AsyncSession = Depends(get_db)):
    # Use db session here
    pass
```

## Security (`security.py`)

Handles password hashing and JWT token operations.

```python
from passlib.context import CryptContext
from jose import jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash"""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generate password hash"""
    return pwd_context.hash(password)

def create_access_token(data: dict) -> str:
    """Create JWT access token"""
    return jwt.encode(data, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
```

### Usage Example:
```python
from core.security import get_password_hash, verify_password

# Hash a password
password_hash = get_password_hash("mysecretpassword")

# Verify a password
is_valid = verify_password("mysecretpassword", password_hash)
```

## Dependencies (`dependencies.py`)

Common dependencies used across the application.

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    """Get current authenticated user"""
    # Token verification logic
    pass
```

### Usage Example:
```python
from core.dependencies import get_current_user

@app.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello, {current_user.username}"}
```

## Error Handling (`exceptions.py`)

Custom exception classes and error handling.

```python
class DatabaseError(Exception):
    """Base class for database-related errors"""
    pass

class NotFoundError(DatabaseError):
    """Raised when a resource is not found"""
    pass
```

### Usage Example:
```python
from core.exceptions import NotFoundError

try:
    user = get_user(user_id)
    if not user:
        raise NotFoundError(f"User {user_id} not found")
except NotFoundError as e:
    raise HTTPException(status_code=404, detail=str(e))
```

## Middleware (`middleware.py`)

Custom middleware for request/response processing.

```python
from fastapi import Request
from time import time

async def add_process_time_header(request: Request, call_next):
    """Add processing time to response headers"""
    start_time = time()
    response = await call_next(request)
    process_time = time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response
```

### Usage Example:
```python
from core.middleware import add_process_time_header

app = FastAPI()
app.middleware("http")(add_process_time_header)
``` 