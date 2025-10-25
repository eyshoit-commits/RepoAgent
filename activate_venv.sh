#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
VENV_DIR="${SCRIPT_DIR}/.venv"

# Check if virtual environment exists
if [ ! -d "$VENV_DIR" ]; then
    echo "Virtual environment not found. Creating a new one..."
    pdm install
fi

# Activate the virtual environment
if [ -f "$VENV_DIR/bin/activate" ]; then
    # For Linux/macOS
    source "$VENV_DIR/bin/activate"
elif [ -f "$VENV_DIR/Scripts/activate" ]; then
    # For Windows
    source "$VENV_DIR/Scripts/activate"
else
    echo "Error: Could not find virtual environment activation script."
    exit 1
fi

echo "Virtual environment activated. Type 'deactivate' to exit."

# Run the shell with the activated environment
$SHELL
