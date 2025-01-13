import os
import sys

# Add the project root to Python path
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

# Import commonly used modules
from .utils.env import load_env_vars
from .client.auth import register_user

# Make these available at package level
__all__ = ['load_env_vars', 'register_user']