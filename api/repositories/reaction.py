from typing import List, Optional
import uuid
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import desc
from ..models.reaction import ReactionDB, Reaction, ReactionCreate
import logging

logger = logging.getLogger(__name__)

class ReactionRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_reaction(
        self,
        reaction_data: ReactionCreate,
        user_id: str
    ) -> Reaction:
        """Create a new reaction"""
        reaction_dict = reaction_data.model_dump()
        reaction_dict.update({
            "id": str(uuid.uuid4()),
            "user_id": user_id
        })
        
        db_reaction = ReactionDB(**reaction_dict)
        self.db.add(db_reaction)
        self.db.commit()
        self.db.refresh(db_reaction)
        
        return Reaction.model_validate(db_reaction)

    def get_by_id(self, reaction_id: str) -> Optional[Reaction]:
        """Get reaction by ID"""
        db_reaction = self.db.query(ReactionDB).filter(ReactionDB.id == reaction_id).first()
        return Reaction.model_validate(db_reaction) if db_reaction else None

    def get_message_reactions(self, message_id: str) -> List[Reaction]:
        """Get all reactions for a message"""
        db_reactions = (
            self.db.query(ReactionDB)
            .filter(ReactionDB.message_id == message_id)
            .order_by(desc(ReactionDB.created_at))
            .all()
        )
        return [Reaction.model_validate(r) for r in db_reactions]

    def delete_reaction(self, reaction_id: str) -> bool:
        """Delete a reaction"""
        result = self.db.query(ReactionDB).filter(ReactionDB.id == reaction_id).delete()
        self.db.commit()
        return result > 0

    def get_user_reaction(self, message_id: str, user_id: str, emoji: str) -> Optional[Reaction]:
        """Get a specific reaction by a user on a message"""
        db_reaction = (
            self.db.query(ReactionDB)
            .filter(
                ReactionDB.message_id == message_id,
                ReactionDB.user_id == user_id,
                ReactionDB.emoji == emoji
            )
            .first()
        )
        return Reaction.model_validate(db_reaction) if db_reaction else None 