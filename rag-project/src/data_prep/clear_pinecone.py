"""
Clear all vectors from Pinecone index before uploading new data.
"""
import os
from dotenv import load_dotenv
from pinecone import Pinecone

def clear_pinecone():
    """Delete all vectors from Pinecone index."""
    # Load environment variables
    load_dotenv()
    
    # Initialize Pinecone
    pc = Pinecone(api_key=os.getenv('PINECONE_API_KEY'))
    
    # Get index
    index_name = os.getenv('PINECONE_INDEX_3')
    index = pc.Index(index_name)
    
    # Get index stats
    stats = index.describe_index_stats()
    total_vectors = stats['total_vector_count']
    
    print(f"Found {total_vectors} vectors in index {index_name}")
    
    if total_vectors == 0:
        print("Index is already empty")
        return
    
    # Delete all vectors
    index.delete(delete_all=True)
    print(f"Successfully cleared all vectors from index {index_name}")

if __name__ == "__main__":
    clear_pinecone() 