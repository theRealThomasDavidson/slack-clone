"""
Authentication and authorization utilities.
"""
from fastapi import HTTPException, Security, Header
from fastapi.security import APIKeyHeader
from typing import Optional, Dict, List
import os
import secrets
from datetime import datetime, timedelta
import jwt
from dotenv import load_dotenv

load_dotenv()

# API key handling
API_KEY_NAME = "X-API-Key"
api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

# Generate JWT secret on startup and keep in memory
JWT_SECRET = secrets.token_urlsafe(32)  # 32 bytes of randomness
JWT_ALGORITHM = "HS256"
JWT_EXPIRATION_HOURS = 24

# Get default API key from environment
DEFAULT_API_KEY = os.getenv("DEFAULT_API_KEY")
if not DEFAULT_API_KEY:
    # Generate a secure default key if none provided
    DEFAULT_API_KEY = secrets.token_urlsafe(24)
    print(f"Warning: No DEFAULT_API_KEY found in environment. Generated temporary key: {DEFAULT_API_KEY}")

# In-memory API key store - Replace with database in production
API_KEYS: Dict[str, Dict] = {
    DEFAULT_API_KEY: {
        "client": "default",
        "rate_limit": 60,  # requests per minute
        "created_at": datetime.utcnow().isoformat(),
        "permissions": ["search", "token"]  # Available permissions: search, token, admin
    }
}

def is_valid_api_key(api_key: str) -> bool:
    """Check if API key is valid."""
    return api_key in API_KEYS

def get_api_key_details(api_key: str) -> Optional[Dict]:
    """Get API key metadata."""
    return API_KEYS.get(api_key)

def has_permission(api_key: str, permission: str) -> bool:
    """Check if API key has specific permission."""
    key_details = get_api_key_details(api_key)
    return key_details is not None and permission in key_details.get("permissions", [])

def generate_api_key() -> str:
    """Generate a new API key."""
    return secrets.token_urlsafe(24)  # 24 bytes = 32 characters

def add_api_key(client: str, rate_limit: int = 60, permissions: List[str] = None) -> str:
    """Add a new API key to the store."""
    api_key = generate_api_key()
    API_KEYS[api_key] = {
        "client": client,
        "rate_limit": rate_limit,
        "created_at": datetime.utcnow().isoformat(),
        "permissions": permissions or ["search"]  # Default to search permission only
    }
    return api_key

async def verify_api_key(api_key: str = Security(api_key_header)) -> str:
    """Verify API key and return it if valid."""
    if not is_valid_api_key(api_key):
        raise HTTPException(
            status_code=401,
            detail="Invalid API key"
        )
    return api_key

async def verify_admin_key(api_key: str = Security(api_key_header)) -> str:
    """Verify API key has admin permissions."""
    if not is_valid_api_key(api_key) or not has_permission(api_key, "admin"):
        raise HTTPException(
            status_code=403,
            detail="Insufficient permissions"
        )
    return api_key

def create_jwt_token(api_key: str) -> str:
    """Create a JWT token for an API key."""
    key_details = get_api_key_details(api_key)
    if not key_details:
        raise ValueError("Invalid API key")
        
    if not has_permission(api_key, "token"):
        raise ValueError("API key does not have token generation permission")
        
    expiration = datetime.utcnow() + timedelta(hours=JWT_EXPIRATION_HOURS)
    
    payload = {
        "sub": api_key,
        "client": key_details["client"],
        "permissions": key_details["permissions"],
        "exp": expiration,
        "iat": datetime.utcnow()
    }
    
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)

def verify_jwt_token(token: str = Header(..., alias="Authorization")) -> Dict:
    """Verify JWT token and return payload."""
    try:
        if not token.startswith("Bearer "):
            raise HTTPException(
                status_code=401,
                detail="Invalid authorization header"
            )
            
        token = token.split(" ")[1]
        payload = jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
        
        # Check if API key is still valid
        api_key = payload["sub"]
        if not is_valid_api_key(api_key):
            raise HTTPException(
                status_code=401,
                detail="API key has been revoked"
            )
            
        return payload
        
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=401,
            detail="Token has expired"
        )
    except jwt.JWTError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        ) 