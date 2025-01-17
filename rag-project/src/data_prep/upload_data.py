from langchain_openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_pinecone import PineconeVectorStore
from langchain.schema import Document
from langchain_community.document_loaders.pdf import PyPDFLoader
from langchain_community.document_loaders import DirectoryLoader
import os
import re
from dotenv import load_dotenv
from datetime import datetime
from src.client.retrieve_data import get_all_channels, get_channel_messages, login_user

load_dotenv()

# Load environment variables
os.environ["PINECONE_API_KEY"] = os.getenv("PINECONE_API_KEY")
os.environ["LANGCHAIN_API_KEY"] = os.getenv("LANGCHAIN_API_KEY")
os.environ["LANGCHAIN_TRACING_V2"] = os.getenv("LANGCHAIN_TRACING_V2")
os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")

def format_message(message):
    """Format a chat message into a structured string."""
    created_at = datetime.fromisoformat(message['created_at'].replace('Z', '+00:00'))
    formatted_time = created_at.strftime('%Y-%m-%d %H:%M:%S')
    
    # Build the message content
    content = f"Time: {formatted_time}\n"
    content += f"Channel: {message.get('channel_id', 'Unknown')}\n"
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

def get_chat_documents():
    """Get all chat messages and convert them to documents."""
    print("Retrieving chat messages...")
    auth_token = login_user()
    if not auth_token:
        print("Failed to login")
        return []
    
    all_messages = []
    channels = get_all_channels(auth_token)
    
    if channels:
        for channel in channels:
            print(f"Fetching messages from channel: {channel['name']}")
            messages = get_channel_messages(channel['id'], auth_token)
            if messages:
                all_messages.extend(messages)
    
    # Convert messages to documents
    documents = []
    for msg in all_messages:
        formatted_content = format_message(msg)
        metadata = {
            "source": "chat",
            "username": msg.get('username'),
            "channel_id": msg.get('channel_id'),
            "timestamp": msg.get('created_at'),
            "message_id": msg.get('id')
        }
        doc = Document(page_content=formatted_content, metadata=metadata)
        documents.append(doc)
    
    print(f"Retrieved {len(documents)} chat messages")
    return documents

def process_script_content(content, filename):
    """Process script content to identify Jesse Pinkman's lines."""
    # Jesse's possible name variations in the script
    jesse_variants = {
        'JESSE', 'PINKMAN', 'JESSE PINKMAN', 'PINKMAN JESSE', 'PINKMAN, JESSE',
        'JESSE (', 'PINKMAN (', 'JESSE:', 'PINKMAN:'
    }
    
    script_parts = []
    current_speaker = None
    current_dialogue = []
    
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if not line:
            continue
        
        # Check if this line is a speaker (all caps)
        if line.isupper() or (line.strip('():.').isupper() and len(line) < 50):
            # If we have Jesse's previous dialogue, save it
            if current_speaker and current_dialogue:
                # Check if any of Jesse's name variations appear in the speaker line
                if any(variant in current_speaker.upper() for variant in jesse_variants):
                    script_parts.append({
                        'speaker': current_speaker,
                        'dialogue': ' '.join(current_dialogue)
                    })
                    print(f"Found Jesse line in {filename}: {' '.join(current_dialogue)[:100]}...")
            current_speaker = line
            current_dialogue = []
        else:
            # Add to current dialogue if we have a speaker
            if current_speaker:
                current_dialogue.append(line)
    
    # Don't forget the last speaker and dialogue
    if current_speaker and current_dialogue:
        if any(variant in current_speaker.upper() for variant in jesse_variants):
            script_parts.append({
                'speaker': current_speaker,
                'dialogue': ' '.join(current_dialogue)
            })
            print(f"Found Jesse line in {filename}: {' '.join(current_dialogue)[:100]}...")
    
    # Convert to documents
    documents = []
    for part in script_parts:
        content = f"Speaker: {part['speaker']}\nDialogue: {part['dialogue']}"
        metadata = {
            "source": "script",
            "filename": filename,
            "speaker": part['speaker'],
            "character": "Jesse Pinkman",
            "type": "dialogue"
        }
        documents.append(Document(page_content=content, metadata=metadata))
    
    return documents

def debug_show_speakers(content, max_lines=100):
    """Show speaker labels for the first few pages."""
    print("\nSpeaker Analysis:")
    print("=" * 50)
    
    current_speaker = None
    lines_shown = 0
    
    for line in content.split('\n'):
        line = line.strip()
        if not line:
            continue
            
        # Check if this line might be a speaker
        if line.isupper() or (line.strip('():.').isupper() and len(line) < 50):
            current_speaker = line
            print(f"\nSPEAKER: {current_speaker}")
        elif current_speaker:
            print(f"LINE: {line}")
        
        lines_shown += 1
        if lines_shown >= max_lines:
            print("\n... (stopping after first few pages)")
            break
    print("=" * 50)

def get_pdf_documents():
    """Get all PDF documents from the scripts directory."""
    print("\nLoading Breaking Bad scripts...")
    script_dir = os.path.join(os.path.dirname(__file__), '..', 'docs', 'Breaking_Bad_Scripts')
    
    if not os.path.exists(script_dir):
        os.makedirs(script_dir)
        print(f"Created scripts directory at {script_dir}")
        return []
    
    # Load PDFs
    loader = DirectoryLoader(script_dir, glob="**/*.pdf", loader_cls=PyPDFLoader)
    raw_documents = loader.load()
    
    print(f"\nFound {len(raw_documents)} documents")
    
    # Show cast list from page 2
    if raw_documents:
        doc = raw_documents[0]
        filename = os.path.basename(doc.metadata.get("source", ""))
        print(f"\nExtracting cast list from page 2 of: {filename}")
        
        # Get page 2 content
        pdf_loader = PyPDFLoader(os.path.join(script_dir, filename))
        pages = pdf_loader.load_and_split()
        
        if len(pages) >= 2:
            print("\nCAST LIST:")
            print("=" * 50)
            cast = []
            current_role = None
            
            lines = [line.strip() for line in pages[1].page_content.split('\n') if line.strip()]
            for line in lines:
                # If line is in all caps, it's likely a character name
                if line.isupper() and len(line) < 50:
                    if current_role:
                        cast.append(current_role)
                    current_role = {"character": line, "description": []}
                elif current_role:
                    current_role["description"].append(line)
            
            # Don't forget the last role
            if current_role:
                cast.append(current_role)
            
            # Print formatted cast list
            for role in cast:
                print(f"\nCHARACTER: {role['character']}")
                if role['description']:
                    print("Description:", " ".join(role['description']))
            
            print("\n" + "=" * 50)
            return []  # Return empty list since we're not processing documents for upload
        else:
            print(f"Script {filename} has fewer than 2 pages")
            return []
    return []

def upload_to_pinecone(documents):
    """Upload documents to Pinecone after splitting them into chunks."""
    if not documents:
        print("No documents to upload")
        return
    
    print(f"\nPreparing {len(documents)} documents for upload...")
    
    # Split documents into smaller chunks
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=100,
        separators=["\n\n", "\n", " ", ""]
    )
    split_docs = text_splitter.split_documents(documents)
    print(f"Split into {len(split_docs)} chunks")
    
    # Upload to Pinecone
    try:
        embeddings = OpenAIEmbeddings(model="text-embedding-3-large")
        vector_store = PineconeVectorStore.from_documents(
            documents=split_docs,
            embedding=embeddings,
            index_name=PINECONE_INDEX
        )
        print("Successfully uploaded documents to Pinecone")
    except Exception as e:
        print(f"Error uploading to Pinecone: {str(e)}")

def main():
    # Only show cast list, skip upload
    print("Extracting cast list from Breaking Bad script...")
    get_pdf_documents()
    print("\nSkipping upload to Pinecone.")

if __name__ == "__main__":
    main() 