from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from ..services.auth import AuthService
from ..models.channel import Channel, ChannelCreate
from ..models.user import User
from ..services.channel import ChannelService

router = APIRouter(prefix="/channels", tags=["channels"])
auth_service = AuthService()
channel_service = ChannelService()

@router.post("/", response_model=Channel)
async def create_channel(
    channel_data: ChannelCreate,
    current_user: User = Depends(auth_service.get_current_user)
):
    """Create a new channel"""
    return await channel_service.create_channel(channel_data, current_user)

@router.get("/", response_model=List[Channel])
async def get_channels(current_user: User = Depends(auth_service.get_current_user)):
    """Get all channels"""
    return channel_service.get_all_channels()

@router.get("/me", response_model=List[Channel])
async def get_my_channels(current_user: User = Depends(auth_service.get_current_user)):
    """Get channels the current user is a member of"""
    return channel_service.get_user_channels(current_user.id)

@router.get("/{channel_name}", response_model=Channel)
async def get_channel(
    channel_name: str,
    current_user: User = Depends(auth_service.get_current_user)
):
    """Get channel by name"""
    return channel_service.get_channel(channel_name)

@router.post("/{channel_name}/join")
async def join_channel(
    channel_name: str,
    current_user: User = Depends(auth_service.get_current_user)
):
    """Join a channel"""
    return await channel_service.join_channel(channel_name, current_user)

@router.post("/{channel_name}/leave")
async def leave_channel(
    channel_name: str,
    current_user: User = Depends(auth_service.get_current_user)
):
    """Leave a channel"""
    return await channel_service.leave_channel(channel_name, current_user)

@router.delete("/{channel_name}")
async def delete_channel(
    channel_name: str,
    current_user: User = Depends(auth_service.get_current_user)
):
    """Delete a channel (owner only)"""
    await channel_service.delete_channel(channel_name, current_user)
    return {"message": "Channel deleted successfully"}

@router.get("/{channel_name}/status")
async def get_subscription_status(
    channel_name: str,
    current_user: User = Depends(auth_service.get_current_user)
):
    """Check if the current user is subscribed to a channel"""
    channel = channel_service.get_channel(channel_name)
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )
    is_subscribed = channel_service.is_user_subscribed(channel.id, current_user.id)
    return {"is_subscribed": is_subscribed} 