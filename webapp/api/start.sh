#!/bin/bash

echo "Waiting for PostgreSQL to be ready..."
while ! nc -z db 5432; do
    sleep 0.1
done
echo "PostgreSQL is ready!"

echo "Running database migrations..."
alembic upgrade head

echo "Starting the application..."
uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload 