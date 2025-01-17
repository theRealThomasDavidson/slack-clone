"""
Scheduler for Breaking Bad character AIs.
Runs each character's check_and_respond at regular intervals.
"""
import schedule
import time
from datetime import datetime
from .run_characters import main as run_all_characters
from ..upload_messages import main as index_messages

def character_job():
    """Run all character AIs and log the time."""
    print(f"\n=== Running character AIs at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    try:
        run_all_characters()
    except Exception as e:
        print(f"Error in character AI job: {str(e)}")
    print(f"=== Job complete at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")

def indexing_job():
    """Run message indexing and log the time."""
    print(f"\n=== Running message indexing at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    try:
        index_messages()
    except Exception as e:
        print(f"Error in indexing job: {str(e)}")
    print(f"=== Indexing complete at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")

def main():
    """Start the scheduler."""
    print("Starting Breaking Bad character AI and indexing scheduler...")
    
    # Schedule the character job to run every minute
    schedule.every(1).minutes.do(character_job)
    
    # Schedule the indexing job to run every 10 minutes
    schedule.every(10).minutes.do(indexing_job)
    
    # Run both jobs immediately once
    character_job()
    indexing_job()
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main() 