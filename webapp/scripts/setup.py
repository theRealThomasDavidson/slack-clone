import os
import time
import subprocess
import sys
import traceback
from pathlib import Path

def wait_for_db():
    print("\n=== Checking Database Connection ===")
    while True:
        try:
            result = subprocess.run(
                ['pg_isready', '-h', 'db', '-p', '5432', '-U', 'postgres', '-q'],
                check=False,
                capture_output=True
            )
            if result.returncode == 0:
                print("✓ Database is ready!")
                break
            print("⚠ Database is unavailable - sleeping")
            if result.stderr:
                print(f"  Error details: {result.stderr.decode()}")
            time.sleep(1)
        except Exception as e:
            print(f"✗ Error checking database connection:")
            print(f"  {str(e)}")
            print(f"  {traceback.format_exc()}")
            time.sleep(1)

def run_command(cmd, description, cwd=None):
    """Run a command and provide detailed feedback"""
    print(f"\n=== {description} ===")
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=True,
            text=True,
            cwd=cwd
        )
        print(f"✓ {description} completed successfully!")
        if result.stdout:
            print("\nOutput:")
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ Error during {description}:")
        print(f"  Exit code: {e.returncode}")
        if e.stdout:
            print("\nCommand output:")
            print(e.stdout)
        if e.stderr:
            print("\nError output:")
            print(e.stderr)
        raise

def main():
    try:
        print("\n=== Starting Setup ===")
        
        # Ensure we're in the right directory
        script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        os.chdir(script_dir)
        print(f"✓ Changed working directory to: {script_dir}")
        
        # Add the current directory to Python path
        sys.path.insert(0, os.getcwd())
        print(f"✓ Added {os.getcwd()} to Python path")
        
        # Wait for database
        wait_for_db()
        
        # Run migrations from the api directory
        run_command(
            ['alembic', 'upgrade', 'head'],
            "Running Database Migrations",
            cwd='api'
        )
        
        # Start the application
        print("\n=== Starting Application ===")
        run_command(
            ['uvicorn', 'api.main:app', '--host', '0.0.0.0', '--port', '8000', '--reload'],
            "Starting API Server"
        )
        
    except Exception as e:
        print("\n✗ Setup failed with error:")
        print(f"  {str(e)}")
        print("\nFull stack trace:")
        print(traceback.format_exc())
        sys.exit(1)

if __name__ == "__main__":
    main() 