from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_pinecone import Pinecone
from langchain.schema import Document
import os
from dotenv import load_dotenv
from datetime import datetime
from src.client.retrieve_data import get_all_channels, get_channel_messages, login_user
from src.client.auth import register_user
from src.data_prep.message_tracker import MessageTracker

load_dotenv()

# Load environment variables
os.environ["PINECONE_API_KEY"] = os.getenv("PINECONE_API_KEY")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")
PINECONE_INDEX = os.getenv("PINECONE_INDEX_3")

def format_message(message):
    """Format a chat message into a structured string."""
    created_at = datetime.fromisoformat(message['created_at'].replace('Z', '+00:00'))
    formatted_time = created_at.strftime('%Y-%m-%d %H:%M:%S')
    
    # Build the message content
    content = f"Time: {formatted_time}\n"
    content += f"Channel: {message.get('channel_name', 'Unknown')}\n"
    content += f"User: {message.get('username', 'Unknown')}\n"
    content += f"Message: {message.get('content', '')}\n"
    
    # Add file information if present
    if message.get('file'):
        content += f"Attachment: {message['file']['filename']}\n"
    
    # Add reactions if present
    if message.get('emojis'):
        reactions = [f"{emoji}: {', '.join(users)}" for emoji, users in message['emojis'].items()]
        content += f"Reactions: {' | '.join(reactions)}\n"
    
    return content

def main():
    print("\n=== Starting message indexing ===")
    
    # Initialize message tracker
    tracker = MessageTracker()
    
    # Get new messages since last check
    print("Retrieving new messages from chat...")
    new_messages = tracker.get_new_messages()
    
    if not new_messages:
        print("No new messages to index")
        print("=== Message indexing complete ===\n")
        return
    
    print(f"Found {len(new_messages)} new messages to index")
    
    # Convert messages to documents
    documents = []
    for msg in new_messages:
        formatted_content = format_message(msg)
        # Create metadata for better retrieval
        metadata = {
            "username": msg.get('username'),
            "channel_id": msg.get('channel_id'),
            "timestamp": msg.get('created_at'),
            "message_id": msg.get('id')
        }
        doc = Document(page_content=formatted_content, metadata=metadata)
        documents.append(doc)
    
    print(f"Going to add {len(documents)} messages to Pinecone")
    
    # Split documents into smaller chunks if needed
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        separators=["\n\n", "\n", " ", ""]
    )
    split_docs = text_splitter.split_documents(documents)
    
    # Upload to Pinecone
    try:
        embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
        vector_store = Pinecone.from_documents(
            documents=split_docs,
            embedding=embeddings,
            index_name=PINECONE_INDEX,
            namespace="chat-messages"
        )
        print("Successfully uploaded messages to Pinecone")
        
        # Update last checked timestamp to latest message
        latest_timestamp = max(msg['created_at'] for msg in new_messages)
        tracker.save_last_checked(latest_timestamp)
        print(f"Updated last checked timestamp to {latest_timestamp}")
        
        print("=== Message indexing complete ===\n")
    except Exception as e:
        print(f"Error uploading to Pinecone: {str(e)}")
        print("=== Message indexing failed ===\n")

if __name__ == "__main__":
    main() 