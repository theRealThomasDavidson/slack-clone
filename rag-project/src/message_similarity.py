from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import Pinecone
import os
from dotenv import load_dotenv
from datetime import datetime

# Load environment variables
load_dotenv()
PINECONE_INDEX = os.getenv("PINECONE_INDEX_3")

def find_similar_messages(sample_message: str, k: int = 20):
    """
    Find messages similar to the sample message using vector similarity search.
    
    Args:
        sample_message (str): The message to find similar messages to
        k (int): Number of similar messages to return (default: 20)
    
    Returns:
        list: List of similar messages with their scores and metadata
    """
    try:
        # Initialize embeddings and vector store
        embeddings = OpenAIEmbeddings(model="text-embedding-ada-002")
        vector_store = Pinecone.from_existing_index(
            index_name=PINECONE_INDEX,
            embedding=embeddings
        )
        
        # Perform similarity search
        results = vector_store.similarity_search_with_score(
            query=sample_message,
            k=k
        )
        
        # Format results
        similar_messages = []
        for doc, score in results:
            metadata = doc.metadata
            similar_messages.append({
                'content': doc.page_content,
                'score': float(score),
                'metadata': {
                    'username': metadata.get('username'),
                    'channel_id': metadata.get('channel_id'),
                    'timestamp': metadata.get('timestamp'),
                    'message_id': metadata.get('message_id')
                }
            })
        
        return similar_messages
        
    except Exception as e:
        print(f"Error searching for similar messages: {str(e)}")
        return []

def main():
    # Example usage
    sample = input("Enter a sample message to find similar messages: ")
    results = find_similar_messages(sample)
    
    print("\n=== Similar Messages ===")
    for i, result in enumerate(results, 1):
        print(f"\nResult {i} (Score: {result['score']:.3f})")
        print("Content:", result['content'])
        print("Metadata:", result['metadata'])

if __name__ == "__main__":
    main() 