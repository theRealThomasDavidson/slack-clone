import os
from dotenv import load_dotenv

def load_env_vars():
    load_dotenv()
    
    required_vars = [
        'chat_app_url',
        'chat_app_username',
        'chat_app_password'
    ]
    
    config = {}
    for var in required_vars:
        value = os.getenv(var)
        if not value:
            raise ValueError(f"Missing required environment variable: {var}")
        config[var] = value
    
    return config