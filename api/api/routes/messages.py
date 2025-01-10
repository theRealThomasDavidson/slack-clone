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
    channel_id: str = Form(...),
    file: Optional[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Create a new message with optional file attachment."""
    try:
        # Convert channel_id to integer
        channel_id_int = int(channel_id)
        
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
            channel_id=channel_id_int,  # Use the converted integer
            user_id=current_user.id
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
            "file": None
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
    """Get a specific message."""
    # Query message with file relationship
    result = await db.execute(
        select(MessageTable)
        .where(MessageTable.id == message_id)
        .options(joinedload(MessageTable.file))
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
            joinedload(MessageTable.file)
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
            "file": None
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