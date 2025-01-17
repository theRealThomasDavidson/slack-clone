"""
Upload processed chunks to Pinecone vector database.
"""
from langchain_pinecone import Pinecone
from langchain_openai import OpenAIEmbeddings
import json
from pathlib import Path
import os
from dotenv import load_dotenv
from tqdm import tqdm

# Get the project root directory (youtube-search)
PROJECT_ROOT = Path(__file__).parent.parent

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")

# Debug: Print path we're looking for .env in
print(f"\nLooking for .env file in: {PROJECT_ROOT / '.env'}")

# Required environment variables
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")
PINECONE_NAMESPACE = os.getenv("PINECONE_NAMESPACE")

# Debug: Print environment variables (safely)
print("\nEnvironment variables found:")
print(f"OPENAI_API_KEY: {'✓ Set' if OPENAI_API_KEY else '✗ Not set'} ({OPENAI_API_KEY[:6] if OPENAI_API_KEY else 'None'}...)")
print(f"PINECONE_API_KEY: {'✓ Set' if PINECONE_API_KEY else '✗ Not set'} ({PINECONE_API_KEY[:6] if PINECONE_API_KEY else 'None'}...)")
print(f"PINECONE_INDEX: {'✓ Set' if PINECONE_INDEX else '✗ Not set'} ({PINECONE_INDEX if PINECONE_INDEX else 'None'})")
print(f"PINECONE_NAMESPACE: {'✓ Set' if PINECONE_NAMESPACE else '✗ Not set'} ({PINECONE_NAMESPACE if PINECONE_NAMESPACE else 'None'})")

if not all([OPENAI_API_KEY, PINECONE_API_KEY, PINECONE_INDEX, PINECONE_NAMESPACE]):
    raise ValueError(
        "Missing required environment variables. Please ensure OPENAI_API_KEY, "
        "PINECONE_API_KEY, PINECONE_INDEX, and PINECONE_NAMESPACE are set."
    )

def upload_chunks(chunks_file: Path):
    """Upload chunks from a processed file to Pinecone."""
    print(f"\nUploading chunks from {chunks_file.name}")
    
    # Load chunks
    with open(chunks_file, 'r', encoding='utf-8') as f:
        chunks = json.load(f)
    
    print(f"Found {len(chunks)} chunks to upload")
    
    # Initialize Pinecone and OpenAI
    embeddings = OpenAIEmbeddings()
    vector_store = Pinecone(
        index_name=PINECONE_INDEX,
        embedding=embeddings,
        namespace=PINECONE_NAMESPACE
    )
    
    # Upload chunks in batches
    batch_size = 100
    for i in tqdm(range(0, len(chunks), batch_size), desc="Uploading batches"):
        batch = chunks[i:i + batch_size]
        texts = [chunk["text"] for chunk in batch]
        metadatas = [chunk["metadata"] for chunk in batch]
        
        try:
            vector_store.add_texts(texts=texts, metadatas=metadatas)
        except Exception as e:
            print(f"\nError uploading batch {i//batch_size + 1}: {str(e)}")
            continue
    
    print("\nUpload completed")

def main():
    """Upload all processed transcript files to Pinecone."""
    processed_dir = PROJECT_ROOT / "data" / "processed"
    
    # Process each transcript file
    for file_path in processed_dir.glob("processed_*.json"):
        upload_chunks(file_path)

if __name__ == "__main__":
    main() 