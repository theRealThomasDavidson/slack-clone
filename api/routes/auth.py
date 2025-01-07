from fastapi import APIRouter, Depends, HTTPException, status
from ..services.auth import AuthService
from ..models.auth import Token, LoginRequest, RegisterRequest
from ..models.user import User, UserResponse

router = APIRouter(prefix="/auth", tags=["auth"])
auth_service = AuthService()

@router.post("/register", response_model=UserResponse)
async def register(user_data: RegisterRequest):
    return await auth_service.create_user(user_data)

@router.post("/login", response_model=Token)
async def login(login_data: LoginRequest):
    return await auth_service.login(login_data.username, login_data.password)

@router.post("/logout")
async def logout(current_user: User = Depends(auth_service.get_current_user)):
    await auth_service.logout(current_user.username)
    return {"message": "Successfully logged out"}

@router.get("/test-auth", response_model=dict)
async def test_auth(current_user: User = Depends(auth_service.get_current_user)):
    """Test endpoint that requires authentication"""
    return {
        "message": "Authentication successful",
        "username": current_user.username
    }