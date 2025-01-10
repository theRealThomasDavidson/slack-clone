from typing import List, Optional
import uuid
import os
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..models.file import FileDB, File, FileCreate
from ..core.config import settings
import logging

logger = logging.getLogger(__name__)

class FileRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_file(
        self,
        file_data: FileCreate,
        uploaded_by: int,
        message_id: int,
        storage_path: str
    ) -> File:
        """Create a new file record"""
        file_dict = file_data.model_dump()
        file_dict.update({
            "uploaded_by": uploaded_by,
            "message_id": message_id,
            "storage_path": storage_path
        })
        
        db_file = FileDB(**file_dict)
        self.db.add(db_file)
        self.db.commit()
        self.db.refresh(db_file)
        
        return File.model_validate(db_file)

    def get_by_id(self, file_id: str) -> Optional[File]:
        """Get file by ID"""
        db_file = self.db.query(FileDB).filter(FileDB.id == file_id).first()
        return File.model_validate(db_file) if db_file else None

    def get_channel_files(self, channel_id: str) -> List[File]:
        """Get all files in a channel"""
        db_files = (
            self.db.query(FileDB)
            .filter(FileDB.channel_id == channel_id)
            .order_by(desc(FileDB.created_at))
            .all()
        )
        return [File.model_validate(f) for f in db_files]

    def delete_file(self, file_id: str) -> bool:
        """Delete a file record"""
        result = self.db.query(FileDB).filter(FileDB.id == file_id).delete()
        self.db.commit()
        return result > 0 