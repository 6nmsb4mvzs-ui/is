#!/bin/bash
# Setup script - copies is_engine to the app's runtime directory

set -e

CONFIG_DIR="$HOME/.idle_slayer_cheat"
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

echo "Setting up Idle Slayer Cheat..."
echo "Config dir: $CONFIG_DIR"
echo "Script dir: $SCRIPT_DIR"

# Create config directory
mkdir -p "$CONFIG_DIR"

# Copy is_engine to config directory
if [ -d "$SCRIPT_DIR/is_engine" ]; then
    echo "Copying is_engine module..."
    cp -r "$SCRIPT_DIR/is_engine" "$CONFIG_DIR/"
    echo "✓ is_engine installed to $CONFIG_DIR/is_engine"
else
    echo "Error: is_engine folder not found at $SCRIPT_DIR/is_engine"
    exit 1
fi

# Install Python requirements
echo "Installing Python dependencies..."
if command -v python3 &> /dev/null; then
    python3 -m pip install -r "$SCRIPT_DIR/requirements.txt" --quiet
    echo "✓ Python packages installed"
else
    echo "Warning: python3 not found. Please install dependencies manually:"
    echo "  python3 -m pip install -r requirements.txt"
fi

echo ""
echo "Setup complete! You can now run the Idle Slayer Cheat app."
