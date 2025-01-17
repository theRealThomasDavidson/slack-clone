"""
Upload dialogue for each Breaking Bad character to their own namespace in Pinecone.
"""
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import os
from dotenv import load_dotenv
from .dialogue_extractor import get_character_documents

def upload_character_dialogue(character_name, username, dialogue_name):
    """Extract and upload a character's dialogue to their namespace."""
    # Load environment variables
    load_dotenv()
    
    # Get character's dialogue documents
    print(f"Extracting {character_name}'s dialogue...")
    character_docs = get_character_documents(dialogue_name)  # Use exact name from dialogue files
    print(f"Found {len(character_docs)} lines from {character_name}")
    
    # Convert to Langchain documents
    documents = []
    for doc in character_docs:
        documents.append(Document(
            page_content=doc['text'],
            metadata={
                'episode': doc['metadata']['episode'],
                'character': dialogue_name,
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
    
    # Initialize embeddings
    embeddings = OpenAIEmbeddings(
        openai_api_key=os.getenv('OPENAI_API_KEY')
    )
    
    # Upload to Pinecone in character's namespace
    print(f"Uploading to {username}'s namespace...")
    vector_store = PineconeVectorStore.from_documents(
        documents=split_docs,
        embedding=embeddings,
        index_name=os.getenv('PINECONE_INDEX_3'),
        namespace=f"{username}-dialogue"
    )
    
    print(f"Upload complete for {character_name}!")
    return vector_store

def main():
    """Upload dialogue for all main characters."""
    characters = [
        ("Walter White", "heisenberg", "walt"),  # Walt or WALTER in scripts
        ("Jesse Pinkman", "pinkman", "jesse"),   # Jesse or JESSE in scripts
        ("Saul Goodman", "saulgoodman", "saul"), # Saul or SAUL in scripts
        ("Skyler White", "skyler", "skyler"),    # Skyler or SKYLER in scripts
        ("Hank Schrader", "hank", "hank")        # Hank or HANK in scripts
    ]
    
    for character_name, username, dialogue_name in characters:
        print(f"\nProcessing {character_name}'s dialogue...")
        try:
            upload_character_dialogue(character_name, username, dialogue_name)
        except Exception as e:
            print(f"Error uploading {character_name}'s dialogue: {str(e)}")
    
    print("\nAll character dialogue uploaded!")

if __name__ == "__main__":
    main() 