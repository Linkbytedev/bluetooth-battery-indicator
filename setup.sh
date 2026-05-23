#!/bin/bash
set -e

# Change to the script's directory
cd "$(dirname "$0")"

# Create a virtual environment with system site packages (for dbus)
echo "Creating virtual environment..."
python3 -m venv --system-site-packages venv

# Activate it
source venv/bin/activate

# Install dependencies
echo "Installing pystray and Pillow..."
pip install --upgrade pip pystray Pillow

echo "Setup complete! Run ./run.sh to start the indicator."
