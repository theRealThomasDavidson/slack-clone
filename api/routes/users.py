from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from ..services.auth import AuthService
from ..models.user import User, UserUpdate
from ..repositories.user import UserRepository

router = APIRouter(prefix="/users", tags=["users"])
auth_service = AuthService()
user_repository = UserRepository()

@router.get("/me", response_model=User)
async def get_current_user(current_user: User = Depends(auth_service.get_current_user)):
    """Get current user's profile"""
    return current_user

@router.get("/{username}", response_model=User)
async def get_user_by_username(
    username: str,
    current_user: User = Depends(auth_service.get_current_user)
):
    """Get user profile by username"""
    user = user_repository.get_by_username(username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user

@router.get("/", response_model=List[User])
async def get_users(current_user: User = Depends(auth_service.get_current_user)):
    """Get all users"""
    return user_repository.get_all()

@router.get("/online", response_model=List[User])
async def get_online_users(current_user: User = Depends(auth_service.get_current_user)):
    """Get all online users"""
    return user_repository.get_online_users()

@router.put("/me", response_model=User)
async def update_user(
    update_data: UserUpdate,
    current_user: User = Depends(auth_service.get_current_user)
):
    """Update current user's profile"""
    updated_user = user_repository.update_user(current_user.id, update_data)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return updated_user

@router.post("/me/status", response_model=User)
async def update_status(
    is_online: bool,
    current_user: User = Depends(auth_service.get_current_user)
):
    """Update current user's online status"""
    updated_user = user_repository.update_status(current_user.id, is_online)
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return updated_user
