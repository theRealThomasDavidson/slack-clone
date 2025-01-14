"""
Jesse-style AI assistant using RAG with Breaking Bad dialogue.
Responds only in private channels, DMs, or replies.
"""
from langchain_openai import OpenAIEmbeddings, OpenAI
from langchain_pinecone import PineconeVectorStore
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
import os
import json
import asyncio
import websockets
import requests
from dotenv import load_dotenv

# Jesse's credentials
CREDENTIALS = {
    "username": "pinkman",
    "email": "jesse@yo.com",
    "password": "sciencebitch"
}

class JesseAI:
    def __init__(self):
        load_dotenv()
        self.base_url = os.getenv('chat_app_url').rstrip('/')
        self.auth_token = None
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = PineconeVectorStore(
            index_name=os.getenv('PINECONE_INDEX_3'),
            embedding=self.embeddings
        )
        self.llm = OpenAI(temperature=0.7)
        
    async def login(self):
        """Login to the chat app."""
        login_url = f"{self.base_url}/api/v1/auth/login"
        response = requests.post(login_url, json=CREDENTIALS)
        if response.status_code == 200:
            self.auth_token = response.json()["access_token"]
            print("Yo, logged in successfully!")
            return True
        print("Login failed, yo!")
        return False
        
    def should_respond(self, message_data):
        """Determine if Jesse should respond to this message."""
        # Respond to DMs
        if message_data.get("is_dm"):
            return True
        # Respond to private channels
        if message_data.get("channel", {}).get("is_private"):
            return True
        # Respond to replies
        if message_data.get("reply_to"):
            return True
        return False
        
    def get_response(self, user_input: str) -> str:
        """Generate Jesse's response using RAG."""
        # Get relevant dialogue
        relevant_docs = self.vector_store.similarity_search(user_input, k=3)
        context = "\n".join([f"- {doc.page_content}" for doc in relevant_docs])
        
        template = """You are Jesse Pinkman from Breaking Bad. Use the following examples of Jesse's dialogue to respond in his authentic voice and style.
Remember his key traits:
- Uses slang and informal language
- Often says "yo" and similar expressions
- Emotional and expressive
- Loyal but sometimes conflicted
- Street-smart but sometimes naive

Context from Jesse's dialogue:
{context}

Current conversation:
Human: {user_input}
Jesse: """

        prompt = PromptTemplate(template=template, input_variables=["context", "user_input"])
        chain = LLMChain(llm=self.llm, prompt=prompt)
        response = chain.run(context=context, user_input=user_input)
        return response.strip()
        
    async def send_message(self, channel_id: str, content: str, reply_to: str = None):
        """Send a message to the chat app."""
        url = f"{self.base_url}/api/v1/messages"
        headers = {"Authorization": f"Bearer {self.auth_token}"}
        data = {
            "channel_id": channel_id,
            "content": content
        }
        if reply_to:
            data["reply_to"] = reply_to
        response = requests.post(url, headers=headers, json=data)
        return response.status_code == 200
        
    async def run(self):
        """Run the Jesse AI chat bot."""
        if not await self.login():
            return
            
        ws_url = f"ws://ec2-18-116-40-33.us-east-2.compute.amazonaws.com:8000/api/v1/ws?token={self.auth_token}"
        
        async with websockets.connect(ws_url) as websocket:
            print("Yo! Jesse's in the house! Connected to chat.")
            
            while True:
                try:
                    message = await websocket.recv()
                    data = json.loads(message)
                    
                    if data["type"] == "message" and self.should_respond(data):
                        response = self.get_response(data["content"])
                        await self.send_message(
                            channel_id=data["channel_id"],
                            content=response,
                            reply_to=data.get("id")
                        )
                except Exception as e:
                    print(f"Error yo: {str(e)}")
                    continue

if __name__ == "__main__":
    jesse = JesseAI()
    asyncio.run(jesse.run())