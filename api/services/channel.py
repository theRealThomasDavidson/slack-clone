from fastapi import HTTPException, status
from ..models.channel import Channel, ChannelCreate
from ..models.user import User
from ..repositories.channel import ChannelRepository
from ..services.message import MessageService
from typing import List

class ChannelService:
    def __init__(self):
        self.repository = ChannelRepository()
        self.message_service = MessageService()

    async def create_channel(self, channel_data: ChannelCreate, user: User) -> Channel:
        """Create a new channel and subscribe the creator"""
        channel = self.repository.create_channel(
            name=channel_data.name,
            description=channel_data.description,
            created_by=user.id
        )
        if not channel:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not create channel"
            )
        
        # Subscribe creator to the channel
        await self.message_service.connection_manager.subscribe_to_channel(user.username, channel.id)
        return channel

    async def join_channel(self, channel_name: str, user: User) -> Channel:
        """Join a channel and subscribe to its messages"""
        channel = self.repository.get_by_name(channel_name)
        if not channel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Channel not found"
            )
        
        updated_channel = self.repository.add_member(channel.id, user.id)
        if not updated_channel:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not join channel"
            )
        
        # Subscribe user to the channel
        await self.message_service.connection_manager.subscribe_to_channel(user.username, channel.id)
        return updated_channel

    async def leave_channel(self, channel_name: str, user: User) -> Channel:
        """Leave a channel and unsubscribe from its messages"""
        channel = self.repository.get_by_name(channel_name)
        if not channel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Channel not found"
            )
        
        if user.id == channel.created_by:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Channel owner cannot leave channel"
            )
        
        updated_channel = self.repository.remove_member(channel.id, user.id)
        if not updated_channel:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Could not leave channel"
            )
        
        # Unsubscribe user from the channel
        await self.message_service.connection_manager.unsubscribe_from_channel(user.username, channel.id)
        return updated_channel

    def get_channel(self, channel_name: str) -> Channel:
        """Get a channel by name"""
        channel = self.repository.get_by_name(channel_name)
        if not channel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Channel not found"
            )
        return channel

    def get_all_channels(self) -> List[Channel]:
        """Get all channels"""
        return self.repository.get_all()

    def get_user_channels(self, user_id: str) -> List[Channel]:
        """Get all channels a user is a member of"""
        return self.repository.get_user_channels(user_id)

    async def delete_channel(self, channel_name: str, user: User) -> None:
        """Delete a channel and clean up subscriptions"""
        channel = self.repository.get_by_name(channel_name)
        if not channel:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Channel not found"
            )
        
        if channel.created_by != user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Only channel owner can delete channel"
            )
        
        # Get all members to unsubscribe them
        members = channel.members
        for member_id in members:
            member = self.repository.get_user(member_id)
            if member:
                await self.message_service.connection_manager.unsubscribe_from_channel(
                    member.username, 
                    channel.id
                )
        
        self.repository.delete(channel.id) 