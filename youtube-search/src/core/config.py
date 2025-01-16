"""
Configuration and environment handling.
"""
import os
from pathlib import Path
from dotenv import load_dotenv

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.parent

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")

# Environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")
PINECONE_NAMESPACE = os.getenv("PINECONE_NAMESPACE")
#PINECONE_NAMESPACE = "heisenberg-dialogue"

def validate_env():
    """Validate required environment variables are set."""
    if not all([OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_INDEX, PINECONE_NAMESPACE]):
        raise ValueError(
            "Missing required environment variables. Please ensure OPENAI_API_KEY, "
            "PINECONE_API_KEY, PINECONE_INDEX, and PINECONE_NAMESPACE are set."
        ) 