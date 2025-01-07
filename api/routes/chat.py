from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from ..services.message import MessageService
from ..services.auth import AuthService
from ..services.channel import ChannelService
from ..models.message import MessageCreate, Message
from ..models.user import User
from ..core.security import verify_token
from ..utils.redis_manager import RedisManager
from typing import List
import logging
from fastapi import status

router = APIRouter(tags=["messages"])
message_service = MessageService()
auth_service = AuthService()
channel_service = ChannelService()
redis_manager = RedisManager()
logger = logging.getLogger(__name__)

@router.post("/messages", response_model=Message)
async def create_message(
    message_data: MessageCreate,
    current_user: User = Depends(auth_service.get_current_user)
):
    """Create a new message"""
    logger.info(f"Received message creation request: {message_data}")
    logger.info(f"From user: {current_user.username} (ID: {current_user.id})")
    
    # Update the message with user info
    message_data.username = current_user.username
    message_data.user_id = current_user.id
    
    # Create the message
    message = await message_service.add_message(message_data)
    logger.info(f"Created message: {message}")
    return message

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
    # Get messages from Redis first
    messages = await redis_manager.get_channel_messages(channel_id)
    if not messages:
        # Fall back to database if no messages in Redis
        messages = message_service.get_channel_messages(channel_id)
    return messages

@router.get("/channels/{channel_name}/messages")
async def get_channel_messages_by_name(
    channel_name: str,
    current_user: User = Depends(auth_service.get_current_user)
):
    """Get messages for a specific channel by name"""
    channel = channel_service.get_channel(channel_name)
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )
    messages = await redis_manager.get_channel_messages(channel.id)
    if not messages:
        messages = message_service.get_channel_messages(channel.id)
    return messages

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
    try:
        # First verify the token is valid
        verified_username = verify_token(token)
        if not verified_username:
            logger.error(f"Invalid token for user {username}")
            await websocket.close(code=4001, reason="Invalid or expired token")
            return
            
        # Then verify username matches
        if username != verified_username:
            logger.error(f"Username mismatch: {username} != {verified_username}")
            await websocket.close(code=4003, reason="Username mismatch")
            return
            
        # Get the user object
        user = auth_service.user_repository.get_by_username(username)
        if not user:
            logger.error(f"User not found: {username}")
            await websocket.close(code=4004, reason="User not found")
            return

        # Connect to Redis manager
        await redis_manager.connect(websocket, username)
        logger.info(f"User {username} connected successfully")

        try:
            # Ensure default channels exist and user is subscribed
            channels = await channel_service.ensure_default_channels(user)
            
            # Subscribe to user's channels
            for channel in channels:
                await redis_manager.subscribe_to_channel(username, channel.id)
                logger.debug(f"Subscribed {username} to channel {channel.id}")

            while True:
                # Receive and process messages
                data = await websocket.receive_json()
                logger.info(f"WebSocket received message: {data}")
                
                # Validate message data
                if not isinstance(data, dict) or 'content' not in data or ('channelId' not in data and 'channel_id' not in data):
                    logger.error(f"Invalid message format: {data}")
                    await websocket.send_json({
                        "error": "Invalid message format. Expected {content, channelId or channel_id}"
                    })
                    continue
                
                # Create and save the message
                try:
                    channel_id = data.get("channel_id") or data.get("channelId")
                    logger.info(f"Creating message in channel {channel_id}: {data['content']}")
                    message_data = MessageCreate(
                        content=data["content"],
                        channel_id=channel_id,
                        username=username,
                        user_id=user.id
                    )
                    
                    # Save the message
                    saved_message = await message_service.add_message(message_data)
                    
                    # Broadcast through Redis
                    await redis_manager.broadcast_to_channel(
                        saved_message.model_dump(),
                        channel_id
                    )
                    
                except Exception as e:
                    logger.error(f"Error processing message: {str(e)}")
                    await websocket.send_json({
                        "error": f"Error processing message: {str(e)}"
                    })
                    
        except WebSocketDisconnect:
            logger.info(f"WebSocket disconnected for user: {username}")
            await redis_manager.disconnect(username)
        except Exception as e:
            logger.error(f"Error in WebSocket message loop: {str(e)}")
            await redis_manager.disconnect(username)
            await websocket.close(code=4002, reason="Message processing error")
            
    except Exception as e:
        logger.error(f"WebSocket connection error: {str(e)}")
        try:
            await websocket.close(code=4000, reason=str(e))
        except:
            pass  # Connection might already be closed 

@router.get("/channels/{channel_name}/messages")
async def get_channel_messages_by_name(
    channel_name: str,
    current_user: User = Depends(auth_service.get_current_user)
):
    """Get messages for a specific channel by name"""
    channel = channel_service.get_channel(channel_name)
    if not channel:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Channel not found"
        )
    messages = message_service.get_channel_messages(channel.id)
    print(f"Found {len(messages)} messages for channel {channel_name} (ID: {channel.id})")
    return messages 