#!/bin/bash
echo "Removing pycache files..."
# Navigate to the parent directory of the script's location
cd "$(dirname "$0")/.."

# Find and remove all __pycache__ directories from the current directory (which is now the parent) and its subdirectories
find . -type d -name "__pycache__" -exec rm -r {} +
