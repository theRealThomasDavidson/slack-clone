"""
Authentication utilities for the chat app
"""
import os
from pathlib import Path
import requests
from dotenv import load_dotenv

# Get the rag-project root directory and load .env
RAG_PROJECT_ROOT = Path(__file__).parent.parent.parent
load_dotenv(RAG_PROJECT_ROOT / '.env')

def login_user(chat_app_url: str, chat_app_username: str, chat_app_password: str) -> str:
    """
    Login to the chat app and return the auth token
    """
    url = f"{chat_app_url.rstrip('/')}/api/v1/auth/login"
    
    # FastAPI OAuth2 expects form data, not JSON
    data = {
        "username": chat_app_username,
        "password": chat_app_password
    }
    
    try:
        response = requests.post(url, data=data)  # Using data= for form data
        if response.status_code == 200:
            result = response.json()
            return f"Bearer {result['access_token']}"  # FastAPI returns access_token
        print(f"Login failed with status {response.status_code}")
        print(f"Response: {response.text}")
        return None
    except Exception as e:
        print(f"Login error: {str(e)}")
        return None

def register_user(username: str, email: str, password: str) -> bool:
    """
    Register a new user in the chat app
    
    Args:
        username: The username for the new user
        email: The email address for the new user
        password: The password for the new user
    """
    chat_app_url = os.getenv("chat_app_url")
    if not chat_app_url:
        print("Error: chat_app_url not found in environment variables")
        return False
        
    url = f"{chat_app_url.rstrip('/')}/api/v1/auth/register"
    data = {
        "username": username,
        "email": email,
        "password": password
    }
    
    try:
        response = requests.post(url, json=data)  # Registration uses JSON
        if response.status_code == 200:
            print(f"Successfully registered user: {username}")
            return True
        print(f"Registration failed with status {response.status_code}")
        print(f"Response: {response.text}")
        return False
    except Exception as e:
        print(f"Registration error: {str(e)}")
        return False

if __name__ == "__main__":
    # First try to register
    register_result = register_user()
    print(f"Registration result: {register_result}")
    
    # Then try to login
    login_result = login_user()
    print(f"Login result: {login_result}")
    if login_result:
        print("Successfully got bearer token!")