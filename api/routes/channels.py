from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from ..services.auth import AuthService
from ..models.channel import Channel, ChannelCreate, ChannelType
from ..models.user import User
from ..services.channel import ChannelService
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(prefix="/channels", tags=["channels"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    auth_service = AuthService()
    user = auth_service.verify_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@router.post("/", response_model=Channel)
async def create_channel(
    channel_data: ChannelCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new channel"""
    channel_service = ChannelService()
    return channel_service.create_channel(
        name=channel_data.name,
        description=channel_data.description,
        created_by=current_user.id,
        channel_type=channel_data.type
    )

@router.get("/", response_model=List[Channel])
async def get_channels(current_user: User = Depends(get_current_user)):
    """Get all channels"""
    channel_service = ChannelService()
    return channel_service.get_all_channels()

@router.get("/me", response_model=List[Channel])
async def get_my_channels(current_user: User = Depends(get_current_user)):
    """Get channels the current user is a member of"""
    channel_service = ChannelService()
    return channel_service.get_user_channels(current_user.id)

@router.get("/{channel_id}", response_model=Channel)
async def get_channel(
    channel_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get channel by ID"""
    channel_service = ChannelService()
    return channel_service.get_channel(channel_id)

@router.post("/{channel_id}/join")
async def join_channel(
    channel_id: str,
    current_user: User = Depends(get_current_user)
):
    """Join a channel"""
    channel_service = ChannelService()
    return channel_service.add_member(channel_id, current_user.id)

@router.post("/{channel_id}/leave")
async def leave_channel(
    channel_id: str,
    current_user: User = Depends(get_current_user)
):
    """Leave a channel"""
    channel_service = ChannelService()
    return channel_service.remove_member(channel_id, current_user.id)

@router.delete("/{channel_id}")
async def delete_channel(
    channel_id: str,
    current_user: User = Depends(get_current_user)
):
    """Delete a channel (owner only)"""
    channel_service = ChannelService()
    channel = channel_service.get_channel(channel_id)
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )
    if channel.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only channel owner can delete channel"
        )
    channel_service.delete_channel(channel_id)
    return {"message": "Channel deleted successfully"}

@router.post("/{channel_id}/ban/{user_id}")
async def ban_user(
    channel_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """Ban a user from a channel"""
    channel_service = ChannelService()
    channel = channel_service.get_channel(channel_id)
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )
    if channel.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only channel owner can ban users"
        )
    return channel_service.set_member_exception(channel_id, user_id)

@router.post("/{channel_id}/unban/{user_id}")
async def unban_user(
    channel_id: str,
    user_id: str,
    current_user: User = Depends(get_current_user)
):
    """Unban a user from a channel"""
    channel_service = ChannelService()
    channel = channel_service.get_channel(channel_id)
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )
    if channel.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only channel owner can unban users"
        )
    return channel_service.remove_member_exception(channel_id, user_id)

@router.post("/{channel_id}/ban-by-username/{username}")
async def ban_user_by_username(
    channel_id: str,
    username: str,
    current_user: User = Depends(get_current_user)
):
    """Ban a user from a channel by username"""
    auth_service = AuthService()
    target_user = auth_service.get_user_by_username(username)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Prevent self-banning
    if target_user.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot ban yourself"
        )
    
    return await ban_user(channel_id, target_user.id, current_user)

@router.post("/{channel_id}/unban-by-username/{username}")
async def unban_user_by_username(
    channel_id: str,
    username: str,
    current_user: User = Depends(get_current_user)
):
    """Unban a user from a channel by username"""
    auth_service = AuthService()
    target_user = auth_service.get_user_by_username(username)
    if not target_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return await unban_user(channel_id, target_user.id, current_user)

@router.get("/{channel_id}/banned-users")
async def get_banned_users(
    channel_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get list of banned users for a channel"""
    channel_service = ChannelService()
    channel = channel_service.get_channel(channel_id)
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )
    
    # Only channel owner can view banned users
    if channel.created_by != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only channel owner can view banned users"
        )
    
    auth_service = AuthService()
    banned_users = []
    for exception in channel.member_exceptions:
        user = auth_service.get_user_by_id(exception.user_id)
        if user:
            banned_users.append({
                "id": user.id,
                "username": user.username,
                "display_name": user.display_name
            })
    
    return banned_users 