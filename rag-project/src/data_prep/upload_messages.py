"""
Upload new chat messages to Pinecone vector store.
Uses message tracker to only process new messages since last check.
"""
import os
from datetime import datetime
from dotenv import load_dotenv
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from .message_tracker import MessageTracker

class MessageUploader:
    def __init__(self):
        load_dotenv()
        self.embeddings = OpenAIEmbeddings()
        self.vector_store = PineconeVectorStore(
            index_name=os.getenv("PINECONE_INDEX_3"),
            embedding=self.embeddings,
            namespace="chat-history"
        )
        self.tracker = MessageTracker()
        
    def format_message(self, msg):
        """Format message for vector store."""
        return {
            'text': f"{msg['username']}: {msg['content']}",
            'metadata': {
                'channel': msg['channel_name'],
                'username': msg['username'],
                'timestamp': msg['created_at'],
                'message_id': msg['id']
            }
        }
        
    def upload_messages(self):
        """Get new messages and upload them to vector store."""
        new_messages = self.tracker.get_new_messages()
        
        if not new_messages:
            print("No new messages to upload")
            return
            
        print(f"\nUploading {len(new_messages)} new messages to vector store...")
        
        # Format messages for vector store
        documents = [self.format_message(msg) for msg in new_messages]
        
        # Upload to vector store
        try:
            self.vector_store.add_texts(
                texts=[doc['text'] for doc in documents],
                metadatas=[doc['metadata'] for doc in documents]
            )
            print("Successfully uploaded messages")
            
            # Update last checked timestamp
            self.tracker.save_last_checked(max(msg['created_at'] for msg in new_messages))
            
        except Exception as e:
            print(f"Error uploading messages: {e}")
            
def main():
    """Run message upload process."""
    uploader = MessageUploader()
    uploader.upload_messages()
    
if __name__ == "__main__":
    main() 