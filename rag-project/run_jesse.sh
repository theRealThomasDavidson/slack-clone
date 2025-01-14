#!/bin/bash

# Change to project directory
cd /home/ubuntu/slack-clone/rag-project

# Activate virtual environment
source .venv/bin/activate

# Run Jesse
python -m src.processing.run_jesse >> jesse.log 2>&1 