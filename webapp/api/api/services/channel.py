"""Channel service."""

from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException, status

from ..models.tables.channel import Channel, channel_members
from ..models.tables.user import User
from ..database import get_db

class ChannelService:
    """Service for managing channels."""

    @staticmethod
    async def create_channel(
        db: AsyncSession,
        name: str,
        description: str | None = None,
        created_by_user: User = None,
        is_private: bool = False,
        members: List[User] = None
    ) -> Channel:
        """Create a new channel."""
        try:
            # Check for existing channel with same name
            result = await db.execute(select(Channel).filter(Channel.name == name))
            if result.scalar_one_or_none():
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Channel with this name already exists"
                )

            # Create new channel
            channel = Channel(
                name=name,
                description=description or "",
                is_private=is_private
            )
            db.add(channel)
            await db.flush()  # Flush to get the channel ID
            
            # Add members if provided, otherwise just add creator for private channels
            if members:
                for member in members:
                    await db.execute(
                        channel_members.insert().values(
                            channel_id=channel.id,
                            user_id=member.id
                        )
                    )
            elif created_by_user and is_private:
                await db.execute(
                    channel_members.insert().values(
                        channel_id=channel.id,
                        user_id=created_by_user.id
                    )
                )
            
            await db.commit()
            await db.refresh(channel)
            return channel
            
        except IntegrityError:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Channel with this name already exists"
            )
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create channel: {str(e)}"
            )

    @staticmethod
    async def get_channel(db: AsyncSession, channel_id: int) -> Optional[Channel]:
        """Get a channel by ID."""
        result = await db.execute(select(Channel).filter(Channel.id == channel_id))
        channel = result.scalar_one_or_none()
        if not channel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Channel not found"
            )
        return channel

    @staticmethod
    async def get_channels(db: AsyncSession) -> List[Channel]:
        """Get all public channels, excluding DM channels."""
        result = await db.execute(
            select(Channel)
            .filter(Channel.is_private == False)
            .filter(~Channel.name.startswith('DM_'))  # Exclude DM channels
        )
        return list(result.scalars().all())

    @staticmethod
    async def get_user_channels(db: AsyncSession, user: User) -> List[Channel]:
        """Get channels where user is a member."""
        result = await db.execute(
            select(Channel)
            .join(channel_members)
            .filter(channel_members.c.user_id == user.id)
        )
        return list(result.scalars().all())

    @staticmethod
    async def join_channel(db: AsyncSession, channel: Channel, user: User) -> Channel:
        """Add a user to a channel."""
        # Check if channel is private and user is not already a member
        if channel.is_private:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot join private channel without invitation"
            )

        # Check if user is already a member
        result = await db.execute(
            select(channel_members).where(
                (channel_members.c.channel_id == channel.id) &
                (channel_members.c.user_id == user.id)
            )
        )
        if result.first() is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this channel"
            )
        
        # Add user to channel
        await db.execute(
            channel_members.insert().values(
                channel_id=channel.id,
                user_id=user.id
            )
        )
        await db.commit()
        await db.refresh(channel)
        return channel

    @staticmethod
    async def leave_channel(db: AsyncSession, channel: Channel, user: User) -> Channel:
        """Remove a user from a channel."""
        # Check if user is a member
        result = await db.execute(
            select(channel_members).where(
                (channel_members.c.channel_id == channel.id) &
                (channel_members.c.user_id == user.id)
            )
        )
        if result.first() is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is not a member of this channel"
            )
        
        # Remove user from channel
        await db.execute(
            channel_members.delete().where(
                (channel_members.c.channel_id == channel.id) &
                (channel_members.c.user_id == user.id)
            )
        )
        await db.commit()
        await db.refresh(channel)
        return channel

    @staticmethod
    async def add_member_to_channel(db: AsyncSession, channel: Channel, user_to_add: User, current_user: User) -> Channel:
        """Add a member to a channel. Only channel members can add new members to private channels."""
        # Check if channel is private
        if channel.is_private:
            # Check if current user is a member
            result = await db.execute(
                select(channel_members).where(
                    (channel_members.c.channel_id == channel.id) &
                    (channel_members.c.user_id == current_user.id)
                )
            )
            if result.first() is None:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Only channel members can add users to private channels"
                )

        # Check if user is already a member
        result = await db.execute(
            select(channel_members).where(
                (channel_members.c.channel_id == channel.id) &
                (channel_members.c.user_id == user_to_add.id)
            )
        )
        if result.first() is not None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User is already a member of this channel"
            )
        
        # Add user to channel
        await db.execute(
            channel_members.insert().values(
                channel_id=channel.id,
                user_id=user_to_add.id
            )
        )
        await db.commit()
        await db.refresh(channel)
        return channel 