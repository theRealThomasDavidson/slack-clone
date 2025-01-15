"""
Breaking Bad Character AI package initialization
"""
import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Load environment variables
RAG_PROJECT_ROOT = Path(__file__).parent.parent
load_dotenv(RAG_PROJECT_ROOT / '.env')

# Import commonly used modules
from .client.auth import register_user

# Make these available at package level
__all__ = ['register_user']