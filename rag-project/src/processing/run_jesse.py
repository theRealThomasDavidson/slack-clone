"""
Run Jesse Pinkman AI to check and respond to messages
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from .character_ai import CharacterAI

# Get the rag-project root directory and load .env
RAG_PROJECT_ROOT = Path(__file__).parent.parent.parent
load_dotenv(RAG_PROJECT_ROOT / '.env')

def main():
    """Run Jesse AI once."""
    jesse = CharacterAI(
        username=os.getenv("JESSE_USERNAME"),
        password=os.getenv("JESSE_PASSWORD"),
        character_name="Jesse Pinkman",
        personality_traits="""
        - Uses slang and informal language (yo, like, etc.)
        - Emotional and expressive
        - Loyal but sometimes conflicted
        - Street-smart but sometimes naive
        - Often reacts based on emotions
        """
    )
    jesse.check_and_respond()

if __name__ == "__main__":
    main() 