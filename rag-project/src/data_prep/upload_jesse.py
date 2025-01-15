"""
Upload Jesse's dialogue to Pinecone for RAG processing.
"""
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import os
from dotenv import load_dotenv

from .dialogue_extractor import get_character_documents

def upload_jesse_dialogue():
    """Extract Jesse's dialogue and upload it to Pinecone."""
    # Load environment variables
    load_dotenv()
    
    # Get Jesse's dialogue documents
    print("Extracting Jesse's dialogue...")
    jesse_docs = get_character_documents('jesse')
    print(f"Found {len(jesse_docs)} lines from Jesse")
    
    # Convert to Langchain documents
    documents = []
    for doc in jesse_docs:
        documents.append(Document(
            page_content=doc['text'],
            metadata={
                'episode': doc['metadata']['episode'],
                'character': 'jesse',
                'source': doc['metadata']['filename'],
                'type': 'dialogue'
            }
        ))
    
    # Split long documents if needed
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        length_function=len,
    )
    split_docs = text_splitter.split_documents(documents)
    print(f"Split into {len(split_docs)} chunks")
    
    # Initialize embeddings with specific model and dimensions
    embeddings = OpenAIEmbeddings(
        openai_api_key=os.getenv('OPENAI_API_KEY')
    )
    
    # Upload to Pinecone
    print("Uploading to Pinecone...")
    vector_store = PineconeVectorStore.from_documents(
        documents=split_docs,
        embedding=embeddings,
        index_name=os.getenv('PINECONE_INDEX_3'),
        namespace="jesse-script"
    )
    
    print("Upload complete!")
    return vector_store

if __name__ == "__main__":
    upload_jesse_dialogue() 