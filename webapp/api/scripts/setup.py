import os
import time
import subprocess
import sys
from pathlib import Path
import shutil

def wait_for_db():
    while True:
        try:
            result = subprocess.run(['pg_isready', '-h', 'db', '-p', '5432', '-U', 'postgres', '-q'],
                                  check=False)
            if result.returncode == 0:
                print("Database is ready!")
                break
            print("Database is unavailable - sleeping")
            time.sleep(1)
        except Exception as e:
            print(f"Error checking database: {e}")
            time.sleep(1)

def create_database():
    """Create database tables directly using SQLAlchemy"""
    print("Creating database tables...")
    from api.database import Base, engine
    import asyncio
    
    async def create_tables():
        async with engine.begin() as conn:
            # Drop all existing tables
            await conn.run_sync(Base.metadata.drop_all)
            # Create all tables fresh
            await conn.run_sync(Base.metadata.create_all)
    
    asyncio.run(create_tables())

def main():
    try:
        os.chdir('/app')
        wait_for_db()
        
        # Create fresh database tables
        create_database()
        
        # Create initial data
        print("Creating initial data...")
        subprocess.run(['python', '/app/scripts/reset_db.py'], check=True)
        
        # Start the application
        print("Starting application...")
        subprocess.run(['uvicorn', 'api.main:app', '--host', '0.0.0.0', '--port', '8000', '--reload'])
    except Exception as e:
        print(f"Error during setup: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 