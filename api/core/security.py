from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from .config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)
    return encoded_jwt

def verify_token(token: str) -> Optional[str]:
    try:
        print(f"Starting token verification for token: {token[:20]}...")
        
        # Decode and validate the token
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
            options={
                "verify_signature": True,  # Verify the signature
                "verify_exp": True,        # Verify expiration
                "verify_sub": True,        # Verify subject claim exists
                "require_exp": True        # Require expiration claim
            }
        )
        print(f"Token decoded successfully. Payload: {payload}")
        
        # Extract and validate username from subject claim
        username: str = payload.get("sub")
        if not username:
            print("Token validation failed: No username in subject claim")
            return None
            
        # Check if token is expired (redundant with verify_exp but explicit)
        exp = payload.get("exp")
        if not exp:
            print("Token validation failed: No expiration claim")
            return None
            
        exp_datetime = datetime.fromtimestamp(exp, tz=timezone.utc)
        current_time = datetime.now(timezone.utc)
        print(f"Token expires at (UTC): {exp_datetime}")
        print(f"Current time (UTC): {current_time}")
        
        if exp_datetime < current_time:
            print(f"Token validation failed: Token expired at {exp_datetime} UTC")
            return None
            
        print(f"Token validation successful for username: {username}")
        return username
    except JWTError as e:
        print(f"JWT validation error: {str(e)}")
        return None 