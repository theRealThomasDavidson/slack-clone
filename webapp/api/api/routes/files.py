"""File routes."""

import os
import shutil
import uuid
import logging
from pathlib import Path
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, Form
from starlette.responses import FileResponse
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from uuid import UUID

from ..database import get_db
from ..models.tables.user import User
from ..models.tables.file import File as FileTable
from ..models.file import File as FileModel
from ..models.tables.message import Message as MessageTable
from ..routes.auth import get_current_user

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/files", tags=["files"])

@router.get("/{file_id}/metadata", response_model=FileModel)
async def get_file_metadata(
    file_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Get file metadata."""
    file = await db.get(FileTable, str(file_id))
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    return file

@router.get("/{file_id}")
async def get_file(
    file_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Download a file."""
    logger.info(f"Download request received for file_id: {file_id} by user: {current_user.username}")
    
    file = await db.get(FileTable, str(file_id))
    logger.info(f"Database query result: {file.__dict__ if file else None}")
    
    if not file:
        logger.warning(f"File {file_id} not found in database")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    
    file_path = Path(file.filepath)
    logger.info(f"Attempting to access file at: {file_path} (absolute: {file_path.absolute()})")
    
    if not file_path.exists():
        logger.error(f"File not found on disk at {file_path}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found on disk"
        )
    
    try:
        return FileResponse(
            path=str(file_path),
            filename=file.filename,
            media_type=file.content_type
        )
    except Exception as e:
        logger.error(f"Error creating FileResponse: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error serving file: {str(e)}"
        )

@router.delete("/{file_id}")
async def delete_file(
    file_id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """Delete a file."""
    file = await db.get(FileTable, str(file_id))
    if not file:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="File not found"
        )
    if file.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot delete another user's file"
        )
    
    # Delete file from disk
    file_path = Path(file.filepath)
    if file_path.exists():
        file_path.unlink()
    
    # Delete database record
    await db.delete(file)
    await db.commit()
    return {"message": "File deleted successfully"} 