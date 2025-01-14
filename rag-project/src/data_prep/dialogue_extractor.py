"""
Extract and format character dialogue from Breaking Bad scripts for RAG processing.
"""
from langchain_community.document_loaders.pdf import PyPDFLoader
import os
from .episode_cast_lists import episode_casts, stage_direction
from .process_dialogue import process_script

def get_character_documents(character_type='jesse'):
    """Extract all lines for a specific character with episode context for vectorization.
    
    Args:
        character_type (str): Type of character to extract ('jesse', 'walt', 'skylar', 'hank', 'saul')
        
    Returns:
        list: List of dictionaries containing character's lines with metadata
    """
    documents = []
    
    for filename, info in episode_casts.items():
        if not info.get('character_mappings'):
            continue
            
        dialogue = process_script(filename, info)
        if dialogue and dialogue[character_type]:
            for line in dialogue[character_type]:
                documents.append({
                    'text': line,
                    'metadata': {
                        'episode': info['title'],
                        'filename': filename,
                        'character': character_type,
                        'type': 'dialogue'
                    }
                })
    
    return documents 