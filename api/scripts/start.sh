#!/bin/bash
set -e

echo "Waiting for database to be ready..."
while ! pg_isready -h db -p 5432 -U postgres -q; do
    echo "Database is unavailable - sleeping"
    sleep 1
done

echo "Database is ready!"

echo "Resetting migrations..."
python /app/scripts/reset_migrations.py

echo "Running database migrations..."
alembic upgrade head || {
    echo "Migration failed! Trying to create database first..."
    python -c "
from api.database import Base, engine
import asyncio
async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
asyncio.run(create_tables())
    "
    echo "Retrying migrations..."
    alembic upgrade head
}

echo "Creating initial data..."
python /app/scripts/reset_db.py || {
    echo "Failed to create initial data!"
    exit 1
}

echo "Starting application..."
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload 