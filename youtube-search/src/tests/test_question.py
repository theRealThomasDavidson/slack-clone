"""
Test the question answering functionality using Heisenberg dialogue.
"""
import asyncio
import os
from dotenv import load_dotenv
from pathlib import Path

from src.search.summarize import TranscriptSummarizer

# Get the project root directory
PROJECT_ROOT = Path(__file__).parent.parent

# Load environment variables
load_dotenv(PROJECT_ROOT / ".env")

# Override namespace for Heisenberg dialogue
os.environ["PINECONE_NAMESPACE"] = "heisenberg-dialogue"

async def main():
    # Initialize summarizer
    summarizer = TranscriptSummarizer()
    
    while True:
        # Get question from user
        print("\nEnter your question about Breaking Bad (or 'quit' to exit):")
        question = input("> ").strip()
        
        if question.lower() in ['quit', 'exit', 'q']:
            break
            
        if not question:
            continue
        
        print(f"\nSearching for answer to: {question}\n")
        
        try:
            # Get answer
            answer = await summarizer.answer_question(question, num_segments=15)
            print("\nAnswer:")
            print("=" * 80)
            print(answer)
            print("=" * 80)
        except Exception as e:
            print(f"\nError: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main()) 