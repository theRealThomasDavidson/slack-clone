from typing import List, Optional
from fastapi import HTTPException, status
from ..models.reaction import Reaction, ReactionCreate
from ..models.user import User
from ..repositories.reaction import ReactionRepository
from ..services.message import MessageService
from ..core.database import SessionLocal
import logging

logger = logging.getLogger(__name__)

class ReactionService:
    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            db = SessionLocal()
            self.repository = ReactionRepository(db)
            self.message_service = MessageService()
            self._initialized = True

    def add_reaction(self, reaction_data: ReactionCreate, current_user: User) -> Reaction:
        """Add a reaction to a message"""
        # Check if message exists and user has access
        message = self.message_service.get_message_by_id(reaction_data.message_id)
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
            
        # Check if user already reacted with this emoji
        existing_reaction = self.repository.get_user_reaction(
            message_id=reaction_data.message_id,
            user_id=current_user.id,
            emoji=reaction_data.emoji
        )
        if existing_reaction:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="You already reacted with this emoji"
            )
            
        return self.repository.create_reaction(reaction_data, current_user.id)

    def remove_reaction(self, reaction_id: str, current_user: User) -> bool:
        """Remove a reaction"""
        reaction = self.repository.get_by_id(reaction_id)
        if not reaction:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reaction not found"
            )
            
        # Only the user who created the reaction can remove it
        if reaction.user_id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to remove this reaction"
            )
            
        return self.repository.delete_reaction(reaction_id)

    def get_message_reactions(self, message_id: str, current_user: User) -> List[Reaction]:
        """Get all reactions for a message"""
        # Check if message exists and user has access
        message = self.message_service.get_message_by_id(message_id)
        if not message:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Message not found"
            )
            
        return self.repository.get_message_reactions(message_id) 