#!/bin/bash

# Copy the reset script to the container
docker cp api/scripts/reset_db.py project-api-1:/app/scripts/

# Run the reset script inside the container
docker exec project-api-1 python /app/scripts/reset_db.py 