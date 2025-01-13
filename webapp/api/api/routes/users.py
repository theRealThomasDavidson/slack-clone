"""User routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List
from pydantic import BaseModel

from ..database import get_db
from ..models.user import User as UserSchema, UserUpdate
from ..models.tables.user import User as UserTable
from ..services.auth import AuthService
from .auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

class UserWithPresence(UserSchema):
    """User schema with presence information."""
    online_status: bool

@router.get("/me", response_model=UserSchema)
async def get_current_user_profile(current_user: UserSchema = Depends(get_current_user)):
    """Get current user's profile."""
    return current_user

@router.put("/me", response_model=UserSchema)
async def update_user_settings(
    settings: UserUpdate,
    current_user: UserSchema = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Update current user's settings."""
    try:
        # Update allowed fields
        for field, value in settings.dict(exclude_unset=True).items():
            setattr(current_user, field, value)
        
        db.add(current_user)
        await db.commit()
        await db.refresh(current_user)
        return current_user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update user settings: {str(e)}"
        )

@router.get("", response_model=List[UserWithPresence])
async def get_users(
    current_user: UserSchema = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all users with their online status."""
    try:
        result = await db.execute(select(UserTable))
        users = result.scalars().all()
        
        # Add presence information
        return [
            UserWithPresence(
                id=user.id,
                username=user.username,
                email=user.email,
                is_active=user.is_active,
                created_at=user.created_at,
                updated_at=user.updated_at,
                online_status=AuthService.is_user_active(user.username)
            )
            for user in users
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve users: {str(e)}"
        )

@router.get("/{username}", response_model=UserSchema)
async def get_user_by_username(
    username: str,
    current_user: UserSchema = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific user by username."""
    user = await AuthService.get_user_by_username(db, username)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user 