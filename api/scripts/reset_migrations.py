import os
import shutil
from pathlib import Path

def reset_migrations():
    # Get the versions directory
    versions_dir = Path(__file__).parent.parent / 'alembic' / 'versions'
    
    # Remove all existing migration files
    if versions_dir.exists():
        for file in versions_dir.glob('*.py'):
            if file.name != '__init__.py':
                file.unlink()
    
    # Create a new migration
    os.system('alembic revision --autogenerate -m "create_all_tables"')
    
    print("Migrations have been reset and recreated.")

if __name__ == "__main__":
    reset_migrations() 