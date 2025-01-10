from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends, status
from datetime import datetime
from ..services.message import MessageService
from ..services.auth import AuthService
from ..services.channel import ChannelService
from ..models.message import MessageCreate, Message
from ..models.user import User
from ..utils.redis_manager import RedisManager
from typing import List, Optional
import logging
from fastapi.security import OAuth2PasswordBearer

router = APIRouter(tags=["messages"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")
logger = logging.getLogger(__name__)

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

@router.post("/messages", response_model=Message)
async def create_message(
    message_data: MessageCreate,
    current_user: User = Depends(get_current_user)
):
    """Create a new message"""
    logger.info(f"Received message creation request: {message_data}")
    logger.info(f"From user: {current_user.username} (ID: {current_user.id})")
    
    message_service = MessageService()
    
    # Update the message with user info
    message_data.username = current_user.username
    message_data.user_id = current_user.id
    
    # Create the message
    message = await message_service.add_message(message_data)
    logger.info(f"Created message: {message}")
    return message

@router.get("/messages", response_model=List[Message])
async def get_messages(current_user: User = Depends(get_current_user)):
    """Get recent messages"""
    message_service = MessageService()
    return message_service.get_recent_messages()

@router.get("/messages/me", response_model=List[Message])
async def get_my_messages(current_user: User = Depends(get_current_user)):
    """Get current user's messages"""
    message_service = MessageService()
    return message_service.get_user_messages(current_user.id)

@router.get("/messages/{channel_id}", response_model=List[Message])
async def get_channel_messages(
    channel_id: str,
    current_user: User = Depends(get_current_user)
):
    """Get messages for a specific channel"""
    message_service = MessageService()
    return message_service.get_channel_messages(channel_id, current_user.id)

@router.post("/messages/clear")
async def clear_messages(current_user: User = Depends(get_current_user)):
    """Clear all messages (for testing only)"""
    message_service = MessageService()
    message_service.clear_messages()
    return {"message": "Messages cleared"}

@router.websocket("/ws/{username}")
async def websocket_endpoint(
    websocket: WebSocket,
    username: str,
    token: str
):
    auth_service = AuthService()
    message_service = MessageService()
    channel_service = ChannelService()
    redis_manager = RedisManager()
    
    try:
        # First verify the token
        user = auth_service.verify_token(token)
        if not user:
            logger.error(f"Invalid token for user {username}")
            await websocket.close(code=4001, reason="Invalid or expired token")
            return
            
        # Then verify username matches
        if username != user.username:
            logger.error(f"Username mismatch: {username} != {user.username}")
            await websocket.close(code=4003, reason="Username mismatch")
            return

        # Connect to Redis manager
        await redis_manager.connect(websocket, username)
        logger.info(f"User {username} connected successfully")

        try:
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
                    
                    # Save and broadcast the message
                    saved_message = await message_service.add_message(message_data)
                    logger.info(f"Message saved and broadcast: {saved_message}")
                    
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