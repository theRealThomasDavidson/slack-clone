"""
Run all Breaking Bad character AIs
"""
import os
import time
import schedule
from pathlib import Path
from dotenv import load_dotenv
from .character_ai import CharacterAI
from ..upload_messages import main as index_messages

# Get the rag-project root directory and load .env
RAG_PROJECT_ROOT = Path(__file__).parent.parent.parent
load_dotenv(RAG_PROJECT_ROOT / '.env')

def run_all_characters():
    """Run all character AIs once."""
    print("\nStarting character AI checks...")
    
    # Jesse Pinkman
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
    
    # Walter White
    walter = CharacterAI(
        username=os.getenv("WALT_USERNAME"),
        password=os.getenv("WALT_PASSWORD"),
        character_name="Walter White",
        personality_traits="""
        - Highly intelligent and calculating
        - Pride and ego drive many decisions
        - Can be manipulative
        - Often justifies actions as "for the family"
        - Becomes increasingly ruthless
        """
    )
    walter.check_and_respond()
    
    # Saul Goodman
    saul = CharacterAI(
        username=os.getenv("SAUL_USERNAME"),
        password=os.getenv("SAUL_PASSWORD"),
        character_name="Saul Goodman",
        personality_traits="""
        - Quick-witted and humorous
        - Uses colorful metaphors and analogies
        - Morally flexible but reliable
        - Always looking for an angle or opportunity
        - Skilled at talking his way out of situations
        """
    )
    saul.check_and_respond()
    
    # Skyler White
    skyler = CharacterAI(
        username=os.getenv("SKYLER_USERNAME"),
        password=os.getenv("SKYLER_PASSWORD"),
        character_name="Skyler White",
        personality_traits="""
        - Intelligent and detail-oriented
        - Protective of family
        - Initially moral but becomes complicit
        - Strong-willed and determined
        - Often suspicious and questioning
        """
    )
    skyler.check_and_respond()
    
    # Hank Schrader
    hank = CharacterAI(
        username=os.getenv("HANK_USERNAME"),
        password=os.getenv("HANK_PASSWORD"),
        character_name="Hank Schrader",
        personality_traits="""
        - Tough and masculine demeanor
        - Dedicated law enforcement officer
        - Uses humor to cope with stress
        - Loyal to family and colleagues
        - Persistent in pursuit of justice
        """
    )
    hank.check_and_respond()
    print("All character checks complete!")

def run_indexing():
    """Run message indexing."""
    try:
        index_messages()
    except Exception as e:
        print(f"Error in indexing job: {str(e)}")

def main():
    """Run the scheduler."""
    print("Starting Breaking Bad Character AI Scheduler")
    
    # Schedule character checks every 15 seconds
    schedule.every(15).seconds.do(run_all_characters)
    
    # Schedule indexing every 10 minutes
    schedule.every(10).minutes.do(run_indexing)
    
    # Run both immediately
    run_all_characters()
    run_indexing()
    
    # Keep running
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main() 