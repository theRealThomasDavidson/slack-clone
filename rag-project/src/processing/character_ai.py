"""
Base class for Breaking Bad character AI assistants.
Each character will inherit from this and customize their personality.
"""
from langchain_openai import OpenAIEmbeddings, OpenAI
from langchain_pinecone import Pinecone
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os
from pathlib import Path
import requests
from dotenv import load_dotenv
from ..client.auth import login_user

# Get the rag-project root directory and load .env
RAG_PROJECT_ROOT = Path(__file__).parent.parent.parent
load_dotenv(RAG_PROJECT_ROOT / '.env')

class CharacterAI:
    def __init__(self, username, password, character_name, personality_traits):
        self.character_name = character_name
        self.personality_traits = personality_traits
        self.username = username
        self.password = password
        self.auth_token = None
        self.base_url = os.getenv("chat_app_url").rstrip('/')
        
        # Initialize auth token
        self.login()
        
        # Initialize AI components
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = Pinecone(
            index_name=os.getenv("PINECONE_INDEX_3"),
            embedding=self.embeddings,
            namespace=f"{username}-dialogue"  # Each character gets their own namespace
        )
        self.llm = OpenAI(temperature=0.7)
        
    def login(self):
        """Login to the chat app."""
        response = login_user(
            chat_app_url=self.base_url,
            chat_app_username=self.username,
            chat_app_password=self.password
        )
        if response:
            self.auth_token = response
            print(f"{self.character_name} logged in successfully!")
            return True
        print(f"{self.character_name} login failed!")
        return False

    def should_check_channel(self, channel):
        """Determine if we should check this channel for messages."""
        # Always check DM channels
        if channel['name'].startswith('DM_'):
            print(f"  ✓ Will check DM channel: {channel['name']}")
            return True
            
        # Check private channels
        if channel.get('is_private', False):
            print(f"  ✓ Will check private channel: {channel['name']}")
            return True
            
        print(f"  ✗ Skipping public channel: {channel['name']}")
        return False
        
    def should_respond(self, message_data):
        """Determine if character should respond to this message."""
        # Don't respond to our own messages
        if message_data.get("username") == self.username:
            print("  ✗ Won't respond to own message")
            return False
            
        # Get channel info
        headers = {"Authorization": self.auth_token}
        channel_url = f"{self.base_url}/api/v1/channels/{message_data['channel_id']}"
        response = requests.get(channel_url, headers=headers)
        
        if response.status_code != 200:
            print(f"  ✗ Couldn't get channel info: {response.status_code}")
            return False
            
        channel = response.json()
        
        # Respond to DMs
        if channel['name'].startswith('DM_'):
            print("  ✓ Will respond to DM")
            return True
            
        # Respond to private channels
        if channel.get('is_private', False):
            print("  ✓ Will respond to private channel message")
            return True
            
        # Respond to replies to character's messages
        if message_data.get("reply_to"):
            reply_url = f"{self.base_url}/api/v1/messages/{message_data['reply_to']}"
            response = requests.get(reply_url, headers=headers)
            if response.status_code == 200:
                original_msg = response.json()
                if original_msg.get("username") == self.username:
                    print("  ✓ Will respond to reply to my message")
                    return True
                    
        print("  ✗ No reason to respond")
        return False
        
    def get_response(self, message_data: dict) -> str:
        """Generate character's response using RAG."""
        user_input = message_data["content"]
        
        # Get conversation context
        headers = {"Authorization": self.auth_token}
        channel_id = message_data["channel_id"]
        
        # Get recent messages for context
        messages_url = f"{self.base_url}/api/v1/messages/channel/{channel_id}"
        response = requests.get(messages_url, headers=headers)
        
        conversation_context = ""
        if response.status_code == 200:
            messages = response.json()
            conversation_context = "\n".join([
                f"{msg['username']}: {msg['content']}"
                for msg in reversed(messages[-5:])  # Get last 5 messages
            ])
        
        # Get relevant dialogue
        relevant_docs = self.vector_store.similarity_search(user_input, k=3)
        dialogue_context = "\n".join([f"- {doc.page_content}" for doc in relevant_docs])
        
        template = f"""You are {self.character_name} from Breaking Bad. Use the following examples of your dialogue and conversation history to respond in your authentic voice and style.

Key character traits:
{self.personality_traits}

Previous dialogue examples:
{{dialogue_context}}

Recent conversation:
{{conversation_context}}

Current message to respond to:
{{user_input}}

{self.character_name}'s response:"""

        prompt = PromptTemplate(
            template=template,
            input_variables=["dialogue_context", "conversation_context", "user_input"]
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        response = chain.run(
            dialogue_context=dialogue_context,
            conversation_context=conversation_context,
            user_input=user_input
        )
        return response.strip()
        
    def send_message(self, channel_id: int, content: str, reply_to: int = None):
        """Send a message to the chat app."""
        url = f"{self.base_url}/api/v1/messages"
        headers = {
            "Authorization": self.auth_token
        }
        
        form_data = {
            "content": content,
            "channel_id": str(channel_id)
        }
            
        print(f"Sending message to channel {channel_id}")
        print(f"Data: {form_data}")
            
        response = requests.post(url, headers=headers, data=form_data)
        if response.status_code == 200:
            print(f"Sent message: {content[:50]}...")
        else:
            print(f"Failed to send message: {response.status_code}")
            print(f"Response: {response.text}")
        return response.status_code == 200
        
    def check_and_respond(self):
        """Check messages once and respond where needed."""
        # Get all channels
        headers = {"Authorization": f"{self.auth_token}"}
        channels_url = f"{self.base_url}/api/v1/channels/me"
        response = requests.get(channels_url, headers=headers)
        
        if response.status_code != 200:
            print(f"Failed to get channels: {response.status_code}")
            return
            
        channels = response.json()
        print(f"\nChecking {len(channels)} channels for messages to respond to...")
        
        for channel in channels:
            print(f"\nChecking channel: {channel['name']}")
            
            if not self.should_check_channel(channel):
                continue
                
            messages_url = f"{self.base_url}/api/v1/messages/channel/{channel['id']}"
            response = requests.get(messages_url, headers=headers)
            
            if response.status_code != 200:
                print(f"Failed to get messages for channel {channel['name']}: {response.status_code}")
                continue
                
            messages = response.json()
            if not messages:
                print("  No messages found")
                continue
                
            last_message = messages[-1]
            print(f"  Last message from {last_message['username']}: {last_message['content'][:50]}...")
            
            if self.should_respond(last_message):
                print("  Generating response...")
                response = self.get_response(last_message)
                print(f"Response: {response}")
                self.send_message(
                    channel_id=last_message['channel_id'],
                    content=response
                ) 