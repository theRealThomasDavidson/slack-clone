"""Channel routes."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from sqlalchemy import select

from ..database import get_db
from ..models.channel import Channel, ChannelCreate
from ..models.tables.user import User
from ..models.tables.message import Message
from ..models.tables.reaction import Reaction as ReactionModel
from ..models.reaction import Reaction, ReactionCreate
from ..services.channel import ChannelService
from ..routes.auth import get_current_user
from ..services.auth import AuthService

router = APIRouter(prefix="/channels", tags=["channels"])

@router.post("", response_model=Channel, status_code=status.HTTP_201_CREATED)
async def create_channel(
    channel: ChannelCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new channel."""
    return await ChannelService.create_channel(
        db=db,
        name=channel.name,
        description=channel.description,
        created_by_user=current_user,
        is_private=channel.is_private
    )

@router.get("", response_model=List[Channel])
async def get_channels(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all public channels."""
    return await ChannelService.get_channels(db)

@router.get("/me", response_model=List[Channel])
async def get_my_channels(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get channels where the current user is a member."""
    return await ChannelService.get_user_channels(db, current_user)

@router.get("/{channel_id}", response_model=Channel)
async def get_channel(
    channel_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific channel by ID."""
    return await ChannelService.get_channel(db, channel_id)

@router.post("/{channel_id}/join", response_model=Channel)
async def join_channel(
    channel_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Join a channel."""
    channel = await ChannelService.get_channel(db, channel_id)
    return await ChannelService.join_channel(db, channel, current_user)

@router.post("/{channel_id}/leave", response_model=Channel)
async def leave_channel(
    channel_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Leave a channel."""
    channel = await ChannelService.get_channel(db, channel_id)
    return await ChannelService.leave_channel(db, channel, current_user)

@router.post("/{channel_id}/members/{user_id}")
async def add_member(
    channel_id: int,
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
) -> Channel:
    """Add a member to a channel."""
    # Get the channel
    channel_service = ChannelService()
    channel = await channel_service.get_channel(db, channel_id)
    
    # Get the user to add
    auth_service = AuthService()
    user_to_add = await auth_service.get_user(db, user_id)
    if not user_to_add:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Add the member
    return await channel_service.add_member_to_channel(db, channel, user_to_add, current_user) 

@router.post("/{channel_id}/messages/{message_id}/reactions", response_model=Reaction)
async def add_reaction(
    channel_id: int,
    message_id: int,
    emoji: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Add or toggle a reaction to a message in a channel."""
    print(f"Adding/toggling reaction - Channel: {channel_id}, Message: {message_id}, Emoji: {emoji}, User: {current_user.username}")
    
    # Verify channel exists and user has access
    channel = await ChannelService.get_channel(db, channel_id)
    if not channel:
        print(f"Channel {channel_id} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )
    print(f"Channel {channel_id} found: {channel.name}")
    
    # Verify message exists and belongs to the channel
    message = await db.get(Message, message_id)
    if not message or message.channel_id != channel_id:
        print(f"Message {message_id} not found in channel {channel_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found in this channel"
        )
    print(f"Message {message_id} found in channel {channel_id}")
    
    # Check if reaction already exists
    existing_reaction = await db.execute(
        select(ReactionModel).where(
            ReactionModel.message_id == message_id,
            ReactionModel.user_id == current_user.id,
            ReactionModel.emoji == emoji
        )
    )
    if existing_reaction.scalar_one_or_none():
        print(f"Reaction already exists for user {current_user.username} on message {message_id}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Reaction already exists"
        )
    
    # Create new reaction
    reaction = ReactionModel(
        emoji=emoji,
        message_id=message_id,
        user_id=current_user.id
    )
    print(f"Creating new reaction: {reaction}")
    db.add(reaction)
    await db.commit()
    await db.refresh(reaction)
    print(f"Reaction created successfully: {reaction}")
    
    # Return reaction with username
    return {
        "id": reaction.id,
        "emoji": reaction.emoji,
        "message_id": reaction.message_id,
        "user_id": reaction.user_id,
        "username": current_user.username,
        "created_at": reaction.created_at
    }

@router.delete("/{channel_id}/messages/{message_id}/reactions/{emoji}")
async def remove_reaction(
    channel_id: int,
    message_id: int,
    emoji: str,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Remove a reaction from a message in a channel."""
    # Verify channel exists and user has access
    channel = await ChannelService.get_channel(db, channel_id)
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )
    
    # Verify message exists and belongs to the channel
    message = await db.get(Message, message_id)
    if not message or message.channel_id != channel_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found in this channel"
        )
    
    # Find and remove the reaction
    reaction = await db.execute(
        select(ReactionModel).where(
            ReactionModel.message_id == message_id,
            ReactionModel.user_id == current_user.id,
            ReactionModel.emoji == emoji
        )
    )
    reaction = reaction.scalar_one_or_none()
    if not reaction:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reaction not found"
        )
    
    await db.delete(reaction)
    await db.commit()
    return {
        "message": "Reaction removed successfully",
        "id": reaction.id,
        "emoji": reaction.emoji,
        "message_id": reaction.message_id,
        "user_id": reaction.user_id,
        "username": current_user.username,
        "created_at": reaction.created_at
    }

@router.get("/{channel_id}/messages/{message_id}/reactions", response_model=List[Reaction])
async def get_message_reactions(
    channel_id: int,
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all reactions for a message in a channel."""
    # Verify channel exists and user has access
    channel = await ChannelService.get_channel(db, channel_id)
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )
    
    # Verify message exists and belongs to the channel
    message = await db.get(Message, message_id)
    if not message or message.channel_id != channel_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found in this channel"
        )
    
    # Get all reactions for the message with usernames
    result = await db.execute(
        select(ReactionModel, User.username)
        .join(User, ReactionModel.user_id == User.id)
        .where(ReactionModel.message_id == message_id)
        .order_by(ReactionModel.created_at)
    )
    reactions_with_users = result.all()
    
    # Construct response with usernames
    reactions = []
    for reaction, username in reactions_with_users:
        reaction_dict = {
            "id": reaction.id,
            "emoji": reaction.emoji,
            "message_id": reaction.message_id,
            "user_id": reaction.user_id,
            "username": username,
            "created_at": reaction.created_at
        }
        reactions.append(reaction_dict)
    
    return reactions 