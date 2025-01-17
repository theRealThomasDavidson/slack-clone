import os
import shutil
from pathlib import Path
import subprocess
import sys

def reset_migrations():
    try:
        # Get the versions directory
        versions_dir = Path(__file__).parent.parent / 'alembic' / 'versions'
        
        # Create versions directory if it doesn't exist
        versions_dir.mkdir(parents=True, exist_ok=True)
        
        # Remove all existing migration files
        if versions_dir.exists():
            for file in versions_dir.glob('*.py'):
                if file.name != '__init__.py':
                    file.unlink()
            
            # Create __init__.py if it doesn't exist
            init_file = versions_dir / '__init__.py'
            if not init_file.exists():
                init_file.touch()
        
        print("Creating new migration...")
        # Use subprocess to get better error handling
        result = subprocess.run(
            ['alembic', 'revision', '--autogenerate', '-m', "create_all_tables"],
            capture_output=True,
            text=True,
            cwd=str(Path(__file__).parent.parent)  # Set working directory to api folder
        )
        
        if result.returncode != 0:
            print("Error creating migration:", result.stderr)
            sys.exit(1)
            
        print("Migration files have been reset and recreated successfully.")
        
    except Exception as e:
        print(f"Error resetting migrations: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    reset_migrations() 