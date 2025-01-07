from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from ..services.message import MessageService
from ..services.auth import AuthService
from ..services.channel import ChannelService
from ..models.message import MessageCreate, Message
from ..models.user import User
from typing import List
import asyncio
import logging

router = APIRouter(tags=["messages"])
message_service = MessageService()
auth_service = AuthService()
channel_service = ChannelService()
logger = logging.getLogger(__name__)

@router.post("/messages", response_model=Message)
async def create_message(
    message_data: MessageCreate,
    current_user: User = Depends(auth_service.get_current_user)
):
    """Create a new message"""
    # Update the message with user info
    message_data.username = current_user.username
    message_data.user_id = current_user.id
    return await message_service.add_message(message_data)

@router.get("/messages", response_model=List[Message])
async def get_messages(current_user: User = Depends(auth_service.get_current_user)):
    """Get recent messages"""
    return message_service.get_recent_messages()

@router.get("/messages/me", response_model=List[Message])
async def get_my_messages(current_user: User = Depends(auth_service.get_current_user)):
    """Get current user's messages"""
    return message_service.get_user_messages(current_user.id)

@router.get("/messages/{channel_id}", response_model=List[Message])
async def get_channel_messages(
    channel_id: str,
    current_user: User = Depends(auth_service.get_current_user)
):
    """Get messages for a specific channel"""
    return message_service.get_channel_messages(channel_id)

@router.post("/messages/clear")
async def clear_messages(current_user: User = Depends(auth_service.get_current_user)):
    """Clear all messages (for testing only)"""
    message_service.clear_messages()
    return {"message": "Messages cleared"}

@router.websocket("/ws/{username}")
async def websocket_endpoint(
    websocket: WebSocket,
    username: str,
    token: str
):
    # Verify token and get user
    try:
        user = await auth_service.get_current_user(token)
        if username != user.username:
            await websocket.close(code=4003, reason="Username mismatch")
            return
    except HTTPException:
        await websocket.close(code=4001, reason="Invalid token")
        return

    await message_service.connection_manager.connect(websocket, username)
    try:
        # Subscribe to user's channels
        user_channels = channel_service.get_user_channels(user.id)
        for channel in user_channels:
            await message_service.connection_manager.subscribe_to_channel(username, channel.id)

        # Send message history to new connection
        recent_messages = message_service.get_recent_messages()
        for message in recent_messages:
            # Only send messages from channels the user is subscribed to
            if message.channel_id in [channel.id for channel in user_channels]:
                await websocket.send_json(message.model_dump())
            
        while True:
            # Receive and process messages
            data = await websocket.receive_json()
            
            # Create and save the message
            message_data = MessageCreate(
                content=data["content"],
                channel_id=data["channel_id"],
                username=username,
                user_id=user.id
            )
            
            # Save the message and let the service handle broadcasting
            await message_service.add_message(message_data)
                
    except WebSocketDisconnect:
        await message_service.connection_manager.disconnect(websocket)
        await auth_service.logout(username) 