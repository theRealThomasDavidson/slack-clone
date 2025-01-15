"""
Jesse-style AI assistant using RAG with Breaking Bad dialogue.
Responds to messages in DMs and channels, focusing on continuing conversations.
"""
from langchain_openai import OpenAIEmbeddings, OpenAI
from langchain_pinecone import Pinecone
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os
import json
import requests
from datetime import datetime, timedelta
from ..utils.env import load_env_vars
from ..client.auth import login_user
from dotenv import load_dotenv

class JesseAI:
    def __init__(self):
        load_dotenv()
        self.config = load_env_vars()
        self.base_url = self.config["chat_app_url"].rstrip('/')
        self.auth_token = None
        self.login()
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = Pinecone(
            index_name=os.getenv("PINECONE_INDEX_3"),
            embedding=self.embeddings
        )
        self.llm = OpenAI(temperature=0.7)
        
    def login(self):
        """Login to the chat app."""
        response = login_user(
            chat_app_url=os.getenv("chat_app_url"),
            chat_app_username="pinkman",
            chat_app_password="sciencebitch"
        )
        if response:
            self.auth_token = response
            print("Yo, logged in successfully!")
            return True
        print("Login failed, yo!")
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
        """Determine if Jesse should respond to this message."""
        # Don't respond to our own messages
        if message_data.get("username") == "pinkman":
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
            
        # Respond to replies to Jesse's messages
        if message_data.get("reply_to"):
            # Get the original message to check if it was Jesse's
            reply_url = f"{self.base_url}/api/v1/messages/{message_data['reply_to']}"
            response = requests.get(reply_url, headers=headers)
            if response.status_code == 200:
                original_msg = response.json()
                if original_msg.get("username") == "pinkman":
                    print("  ✓ Will respond to reply to my message")
                    return True
                    
        print("  ✗ No reason to respond")
        return False
        
    def get_response(self, message_data: dict) -> str:
        """Generate Jesse's response using RAG."""
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
        
        # Get relevant dialogue from both namespaces
        bb_docs = self.vector_store.similarity_search(user_input, k=2, namespace="jesse-script")  # Breaking Bad dialogue
        chat_docs = self.vector_store.similarity_search(user_input, k=2, namespace="chat-history")  # Chat history
        
        # Combine and format both sets of context
        bb_context = "\n".join([f"- {doc.page_content}" for doc in bb_docs])
        chat_context = "\n".join([f"- {doc.page_content}" for doc in chat_docs])
        
        template = """You are Jesse Pinkman from Breaking Bad. Use the following examples of Jesse's dialogue and conversation history to respond in his authentic voice and style.
Remember his key traits:
- Uses slang and informal language (yo, like, etc.)
- Emotional and expressive
- Loyal but sometimes conflicted
- Street-smart but sometimes naive
- Often reacts based on emotions

Breaking Bad dialogue examples:
{bb_context}

Previous chat conversations:
{chat_context}

Recent conversation:
{conversation_context}

Current message to respond to:
{user_input}

Jesse's response:"""

        prompt = PromptTemplate(
            template=template,
            input_variables=["bb_context", "chat_context", "conversation_context", "user_input"]
        )
        
        chain = LLMChain(llm=self.llm, prompt=prompt)
        response = chain.run(
            bb_context=bb_context,
            chat_context=chat_context,
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
        
        # Build form data
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
            
            # First check if we should even look at this channel
            if not self.should_check_channel(channel):
                continue
                
            # Get recent messages
            messages_url = f"{self.base_url}/api/v1/messages/channel/{channel['id']}"
            response = requests.get(messages_url, headers=headers)
            
            if response.status_code != 200:
                print(f"Failed to get messages for channel {channel['name']}: {response.status_code}")
                continue
                
            messages = response.json()
            if not messages:
                print("  No messages found")
                continue
                
            # Get the last message
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
            else:
                print("  No response needed")

def main():
    """Run the Jesse AI bot for one pass."""
    jesse = JesseAI()
    jesse.check_and_respond()

if __name__ == "__main__":
    main() 
