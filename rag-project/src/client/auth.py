import requests
from src.utils.env import load_env_vars

def register_user(chat_app_url=None, chat_app_username=None, chat_app_password=None):
    config = load_env_vars()
    if chat_app_url is None:
        chat_app_url = config['chat_app_url']
    if chat_app_username is None:
        chat_app_username = config['chat_app_username']
    if chat_app_password is None:
        chat_app_password = config['chat_app_password']

    url = f"{chat_app_url.rstrip('/')}/api/v1/auth/register"
    
    data = {
        "username": chat_app_username,
        "password": chat_app_password,
        "email": f"{chat_app_username}@example.com"  # or we can add email to .env
    }
    
    print(f"Attempting to register user at: {url}")
    print(f"With data: {data}")
    
    try:
        response = requests.post(url, json=data)
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Registration failed: {e}")
        return None

def login_user(chat_app_url=None, chat_app_username=None, chat_app_password=None):
    config = load_env_vars()
    if chat_app_url is None:
        chat_app_url = config['chat_app_url']
    if chat_app_username is None:
        chat_app_username = config['chat_app_username']
    if chat_app_password is None:
        chat_app_password = config['chat_app_password']
    
    url = f"{chat_app_url.rstrip('/')}/api/v1/auth/login"
    
    # FastAPI OAuth2 expects form data, not JSON
    data = {
        "username": chat_app_username,
        "password": chat_app_password
    }
    
    print(f"Attempting to login at: {url}")
    print(f"With username: {data['username']}")
    
    try:
        response = requests.post(url, data=data)  # Using data= for form data
        print(f"Response status: {response.status_code}")
        print(f"Response body: {response.text}")
        response.raise_for_status()
        result = response.json()
        return f"Bearer {result['access_token']}"
    except requests.exceptions.RequestException as e:
        print(f"Login failed: {e}")
        return None

if __name__ == "__main__":
    # First try to register
    register_result = register_user()
    print(f"Registration result: {register_result}")
    
    # Then try to login
    login_result = login_user()
    print(f"Login result: {login_result}")
    if login_result:
        print("Successfully got bearer token!")