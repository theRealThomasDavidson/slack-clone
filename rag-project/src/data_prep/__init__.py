"""
Data preparation modules for the Breaking Bad RAG project.
"""

from .dialogue_extractor import get_character_documents
from .process_dialogue import get_character_lines, process_script
from .episode_cast_lists import episode_casts, stage_direction
from .upload_jesse import upload_jesse_dialogue

__all__ = [
    'get_character_documents',  # Get formatted documents for a character
    'get_character_lines',      # Get raw dialogue lines for a character
    'process_script',          # Process a single script file
    'episode_casts',          # Episode metadata and character mappings
    'stage_direction',        # Common stage direction indicators
    'upload_jesse_dialogue',  # Upload Jesse's dialogue to Pinecone
] 