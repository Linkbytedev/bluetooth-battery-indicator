#!/bin/bash

# Change to the script's directory
cd "$(dirname "$0")"

# Activate the virtual environment
source venv/bin/activate

# Run the indicator
python3 indicator.py
