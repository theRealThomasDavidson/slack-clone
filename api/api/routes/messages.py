"""Message routes."""

import os
import shutil
import uuid
import logging
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import joinedload
import re

from ..database import get_db
from ..models.tables.user import User
from ..models.tables.message import Message as MessageTable
from ..models.tables.reaction import Reaction as ReactionTable
from ..models.tables.file import File as FileTable
from ..models.message import Message, MessageCreate, FileInfo
from ..routes.auth import get_current_user

router = APIRouter(prefix="/messages", tags=["messages"])

# Configure upload settings
UPLOAD_DIR = Path("uploads")
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

# Create uploads directory if it doesn't exist
UPLOAD_DIR.mkdir(exist_ok=True)

def extract_file_id(content: str) -> Optional[str]:
    """Extract file ID from message content."""
    match = re.search(r'\[file:([^\]]+)\]', content)
    return match.group(1) if match else None

@router.post("/", response_model=Message)
async def create_message(
    content: str = Form(...),
    channel_id: Optional[str] = Form(None),
    parent_id: Optional[str] = Form(None),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new message with optional file attachment and thread support."""
    try:
        # Convert IDs to integers if provided
        channel_id_int = int(channel_id) if channel_id else None
        parent_id_int = int(parent_id) if parent_id else None
        
        # If it's a thread reply, get the parent message's channel
        if parent_id_int and not channel_id_int:
            parent_message = await db.get(MessageTable, parent_id_int)
            if not parent_message:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Parent message not found"
                )
            channel_id_int = parent_message.channel_id
        
        # Handle file upload if present
        db_file = None
        if file:
            # Read file to check size
            contents = await file.read()
            if len(contents) > MAX_FILE_SIZE:
                raise HTTPException(
                    status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                    detail=f"File too large. Maximum size is {MAX_FILE_SIZE/1024/1024}MB"
                )
            
            # Generate unique filename
            original_extension = Path(file.filename).suffix
            unique_filename = f"{uuid.uuid4()}{original_extension}"
            file_path = UPLOAD_DIR / unique_filename
            
            # Save file
            with open(file_path, "wb") as f:
                f.write(contents)
            
            # Create file record without committing
            db_file = FileTable(
                filename=file.filename,
                filepath=str(file_path),
                content_type=file.content_type,
                size=len(contents),
                user_id=current_user.id
            )
            db.add(db_file)
            await db.flush()  # Get file ID without committing
            
            # Update content to include file reference
            content = f"{content}\nUploaded file: {file.filename} ({len(contents)/1024:.1f} KB) [file:{db_file.id}]"
        
        # Create message
        db_message = MessageTable(
            content=content,
            channel_id=channel_id_int,
            user_id=current_user.id,
            parent_id=parent_id_int
        )
        db.add(db_message)
        await db.flush()  # Get message ID without committing
        
        # Link file to message if present
        if db_file:
            db_file.message_id = db_message.id
        
        # Commit everything
        await db.commit()
        await db.refresh(db_message)
        
        # Prepare response data
        response_data = {
            "id": db_message.id,
            "content": db_message.content,
            "channel_id": db_message.channel_id,
            "user_id": db_message.user_id,
            "created_at": db_message.created_at,
            "updated_at": db_message.updated_at,
            "username": current_user.username,
            "emojis": {},
            "file": None,
            "parent_id": db_message.parent_id
        }
        
        # Add file info if present
        if db_file:
            response_data["file"] = {
                "id": str(db_file.id),
                "filename": db_file.filename,
                "size": db_file.size,
                "content_type": db_file.content_type
            }
        
        # Return response model
        return Message(**response_data)
            
    except Exception as e:
        # Clean up file if saved
        if 'file_path' in locals() and file_path.exists():
            file_path.unlink()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )

@router.get("/{message_id}", response_model=Message)
async def get_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific message with its replies."""
    # Query message with file and replies relationships
    result = await db.execute(
        select(MessageTable)
        .where(MessageTable.id == message_id)
        .options(
            joinedload(MessageTable.file),
            joinedload(MessageTable.replies).joinedload(MessageTable.file),
            joinedload(MessageTable.replies).joinedload(MessageTable.reactions).joinedload(ReactionTable.user)
        )
    )
    message = result.unique().scalar_one_or_none()
    
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    
    # Get the user and add username to the response
    user = await db.get(User, message.user_id)
    setattr(message, 'username', user.username if user else "System")
    
    # Add file info if present
    if message.file:
        setattr(message, 'file', FileInfo(
            id=str(message.file.id),  # Convert UUID to string
            filename=message.file.filename,
            size=message.file.size,
            content_type=message.file.content_type
        ))
    else:
        setattr(message, 'file', None)
    
    # Initialize empty emojis dict
    setattr(message, 'emojis', {})
    
    # Process replies
    replies = []
    for reply in message.replies:
        reply_user = await db.get(User, reply.user_id)
        reply_username = reply_user.username if reply_user else "System"
        
        # Format reactions for reply
        emoji_data = {}
        for reaction in reply.reactions:
            if reaction.emoji not in emoji_data:
                emoji_data[reaction.emoji] = []
            if reaction.user:
                emoji_data[reaction.emoji].append(reaction.user.username)
        
        reply_data = {
            "id": reply.id,
            "content": reply.content,
            "channel_id": reply.channel_id,
            "user_id": reply.user_id,
            "created_at": reply.created_at,
            "updated_at": reply.updated_at,
            "username": reply_username,
            "emojis": emoji_data,
            "file": None,
            "parent_id": reply.parent_id,
            "parent_message": None
        }
        
        # Add file info if present
        if reply.file:
            reply_data["file"] = {
                "id": str(reply.file.id),
                "filename": reply.file.filename,
                "size": reply.file.size,
                "content_type": reply.file.content_type
            }
        
        replies.append(Message(**reply_data))
    
    setattr(message, 'replies', replies)
    setattr(message, 'replies_count', len(replies))
    
    return message

@router.delete("/{message_id}")
async def delete_message(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a message."""
    message = await db.get(MessageTable, message_id)
    if not message:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Message not found"
        )
    if message.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete another user's message"
        )
    await db.delete(message)
    await db.commit()
    return {"message": "Message deleted successfully"}

@router.get("/channel/{channel_id}", response_model=List[Message])
async def get_channel_messages(
    channel_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all messages in a channel."""
    # Query messages with reactions, users, and files
    result = await db.execute(
        select(MessageTable)
        .where(MessageTable.channel_id == channel_id)
        .options(
            joinedload(MessageTable.reactions).joinedload(ReactionTable.user),
            joinedload(MessageTable.file),
            joinedload(MessageTable.replies)
        )
        .order_by(MessageTable.created_at)
    )
    messages = result.unique().scalars().all()
    
    # Process each message
    response_messages = []
    for message in messages:
        # Get message author's username
        user = await db.get(User, message.user_id)
        username = user.username if user else "System"
        
        # Format reactions as {emoji: [usernames]}
        emoji_data = {}
        for reaction in message.reactions:
            if reaction.emoji not in emoji_data:
                emoji_data[reaction.emoji] = []
            if reaction.user:
                emoji_data[reaction.emoji].append(reaction.user.username)
        
        # Prepare message data
        message_data = {
            "id": message.id,
            "content": message.content,
            "channel_id": message.channel_id,
            "user_id": message.user_id,
            "created_at": message.created_at,
            "updated_at": message.updated_at,
            "username": username,
            "emojis": emoji_data,
            "file": None,
            "parent_id": message.parent_id,
            "replies_count": len(message.replies)
        }
        
        # Add file info if present
        if message.file:
            message_data["file"] = {
                "id": str(message.file.id),
                "filename": message.file.filename,
                "size": message.file.size,
                "content_type": message.file.content_type
            }
        
        response_messages.append(Message(**message_data))
    
    return response_messages 

@router.get("/thread/{message_id}", response_model=List[Message])
async def get_thread_messages(
    message_id: int,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get all messages in a thread."""
    # Query messages with reactions, users, files, and parent messages
    result = await db.execute(
        select(MessageTable)
        .where(MessageTable.parent_id == message_id)
        .options(
            joinedload(MessageTable.reactions).joinedload(ReactionTable.user),
            joinedload(MessageTable.file),
            joinedload(MessageTable.parent_message)
        )
        .order_by(MessageTable.created_at)
    )
    messages = result.unique().scalars().all()
    
    # Process each message
    response_messages = []
    for message in messages:
        # Get message author's username
        user = await db.get(User, message.user_id)
        username = user.username if user else "System"
        
        # Format reactions as {emoji: [usernames]}
        emoji_data = {}
        for reaction in message.reactions:
            if reaction.emoji not in emoji_data:
                emoji_data[reaction.emoji] = []
            if reaction.user:
                emoji_data[reaction.emoji].append(reaction.user.username)
        
        # Prepare message data
        message_data = {
            "id": message.id,
            "content": message.content,
            "channel_id": message.channel_id,
            "user_id": message.user_id,
            "created_at": message.created_at,
            "updated_at": message.updated_at,
            "username": username,
            "emojis": emoji_data,
            "file": None,
            "parent_id": message.parent_id,
            "parent_message": None
        }
        
        # Add file info if present
        if message.file:
            message_data["file"] = {
                "id": str(message.file.id),
                "filename": message.file.filename,
                "size": message.file.size,
                "content_type": message.file.content_type
            }
        
        # Add parent message info if present
        if message.parent_message:
            parent_user = await db.get(User, message.parent_message.user_id)
            parent_username = parent_user.username if parent_user else "System"
            message_data["parent_message"] = {
                "id": message.parent_message.id,
                "content": message.parent_message.content,
                "channel_id": message.parent_message.channel_id,
                "user_id": message.parent_message.user_id,
                "username": parent_username,
                "created_at": message.parent_message.created_at,
                "updated_at": message.parent_message.updated_at,
                "emojis": {},  # We don't need reactions for parent messages in threads
                "file": None,  # We don't need file info for parent messages in threads
                "parent_id": message.parent_message.parent_id
            }
        
        response_messages.append(Message(**message_data))
    
    return response_messages 