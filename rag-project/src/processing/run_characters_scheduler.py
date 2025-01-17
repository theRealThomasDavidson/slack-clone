"""
Scheduler for Breaking Bad character AIs.
Runs each character's check_and_respond at regular intervals.
"""
import schedule
import time
from datetime import datetime
from .run_characters import main as run_all_characters

def job():
    """Run all character AIs and log the time."""
    print(f"\n=== Running character AIs at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===")
    try:
        run_all_characters()
    except Exception as e:
        print(f"Error in character AI job: {str(e)}")
    print(f"=== Job complete at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} ===\n")

def main():
    """Start the scheduler."""
    print("Starting Breaking Bad character AI scheduler...")
    
    # Schedule the job to run every minute
    schedule.every(1).minutes.do(job)
    
    # Run the job immediately once
    job()
    
    # Keep the script running
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main() 