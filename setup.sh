#!/bin/bash

# Terminal Agent Setup Script
# This script adds the 'q' function to your shell configuration

set -e

# Get the current directory (where the terminal-assistant project is located)
PROJECT_DIR=$(pwd)

# Function to add to shell config
Q_FUNCTION="
# Terminal agent alias
q() {
    local current_dir=$(pwd)
    cd $PROJECT_DIR
    uvx --from . my-terminal-agent "$@"
    cd "$current_dir"
}
"

# Detect shell and config file
if [[ "$SHELL" == *"zsh"* ]] || [[ -n "$ZSH_VERSION" ]]; then
    SHELL_NAME="zsh"
    CONFIG_FILE="$HOME/.zshrc"
elif [[ "$SHELL" == *"bash"* ]] || [[ -n "$BASH_VERSION" ]]; then
    SHELL_NAME="bash"
    CONFIG_FILE="$HOME/.bashrc"
    # Also check for .bash_profile on macOS
    if [[ "$OSTYPE" == "darwin"* ]] && [[ -f "$HOME/.bash_profile" ]]; then
        CONFIG_FILE="$HOME/.bash_profile"
    fi
else
    echo "Unsupported shell: $SHELL"
    echo "Please manually add the following to your shell configuration:"
    echo "$Q_FUNCTION"
    exit 1
fi

echo "Detected shell: $SHELL_NAME"
echo "Config file: $CONFIG_FILE"

# Clean UV cache to ensure fresh installation
echo "Cleaning UV cache..."
uv cache clean

# Check if the function already exists
if grep -q "# Terminal agent alias" "$CONFIG_FILE" 2>/dev/null; then
    echo "Terminal agent function already exists in $CONFIG_FILE"
    echo "Skipping installation."
    exit 0
fi

# Add the function to the config file
echo "Adding 'q' function to $CONFIG_FILE..."
echo "$Q_FUNCTION" >> "$CONFIG_FILE"

echo "✅ Setup complete!"
echo ""
echo "To start using the 'q' command, either:"
echo "  1. Run: source $CONFIG_FILE"
echo "  2. Or restart your terminal"
echo ""
echo "Usage: q <your query>"
echo "Example: q hello world"