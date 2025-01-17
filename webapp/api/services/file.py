import os
import uuid
import shutil
from typing import List, Optional
from fastapi import UploadFile, HTTPException, status
from ..models.file import File, FileCreate
from ..models.user import User
from ..repositories.file import FileRepository
from ..services.message import MessageService
from ..models.message import MessageCreate
from ..core.database import SessionLocal
import logging

logger = logging.getLogger(__name__)

class FileService:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            db = SessionLocal()
            self.repository = FileRepository(db)
            self.message_service = MessageService()
            self._initialized = True

    async def upload_file(
        self,
        file: UploadFile,
        channel_id: str,
        current_user: User,
        message_content: str = ""
    ) -> File:
        """Upload a file and create associated message"""
        try:
            # Create directory if it doesn't exist
            os.makedirs(f"uploads/{channel_id}", exist_ok=True)
            
            # Generate UUID for the file
            file_id = uuid.uuid4()
            
            # Save file to disk with the UUID
            storage_path = f"uploads/{channel_id}/{file_id}_{file.filename}"
            with open(storage_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            
            # Get file size
            file_size = os.path.getsize(storage_path)
            
            # Create message for the file
            message = await self.message_service.add_message(
                MessageCreate(
                    content=message_content,
                    channel_id=channel_id,
                    username=current_user.username,
                    user_id=current_user.id
                )
            )
            
            # Create file record
            file_data = FileCreate(
                filename=file.filename,
                size=file_size,
                content_type=file.content_type or "application/octet-stream",
                channel_id=channel_id
            )
            
            db_file = self.repository.create_file(
                file_data=file_data,
                uploaded_by=current_user.id,
                message_id=message.id,
                storage_path=storage_path
            )
            
            return db_file
            
        except Exception as e:
            logger.error(f"Error uploading file: {e}")
            # Clean up file if it was saved
            if 'storage_path' in locals():
                try:
                    os.remove(storage_path)
                except:
                    pass
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error uploading file"
            )

    def get_file(self, file_id: str, current_user: User) -> tuple[File, str]:
        """Get file metadata and path"""
        file = self.repository.get_by_id(file_id)
        if not file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
            
        # Check if user has access to the channel
        if not self.message_service.channel_repository.get_by_id(file.channel_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Channel not found"
            )
            
        return file, file.storage_path

    def get_channel_files(self, channel_id: str, current_user: User) -> List[File]:
        """Get all files in a channel"""
        # Check if user has access to the channel
        if not self.message_service.channel_repository.get_by_id(channel_id):
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Channel not found"
            )
            
        return self.repository.get_channel_files(channel_id)

    def delete_file(self, file_id: str, current_user: User) -> bool:
        """Delete a file"""
        file = self.repository.get_by_id(file_id)
        if not file:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="File not found"
            )
            
        # Check if user is file owner or channel owner
        channel = self.message_service.channel_repository.get_by_id(file.channel_id)
        if not channel or (file.uploaded_by != current_user.id and channel.created_by != current_user.id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to delete this file"
            )
            
        # Delete physical file
        try:
            os.remove(file.storage_path)
        except Exception as e:
            logger.error(f"Error deleting file from disk: {e}")
            
        # Delete database record
        return self.repository.delete_file(file_id) 