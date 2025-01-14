#!/bin/bash


# Change to project directory
SCRIPT_DR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &&pwd )"
cd "$SCRIPT_DIR"

# Activate virtual environment
source .venv/bin/activate

# Run Jesse
python3 -m src.processing.run_jesse >> jesse.log 2>&1 
