#!/bin/bash

# Exit on error
set -e

echo "Checking prerequisites..."

# Check for required commands
check_command() {
    if ! command -v "$1" &> /dev/null; then
        echo "Error: $1 is required but not installed."
        case "$1" in
            wget)
                echo "Install it using: brew install wget"
                ;;
            *)
                echo "Please install $1 to continue."
                ;;
        esac
        exit 1
    fi
}

check_command wget

# Installation directory
INSTALL_DIR="$HOME/.local/bin"
BINARY_NAME="quicklook_generator"

# Use the raw GitHub URL for the latest release
# TODO: Replace this with your actual release URL when you create a GitHub release
BINARY_URL="https://raw.githubusercontent.com/anegg0/quicklook-generator/main/dist/quicklook_generator"

echo "Setting up quicklook_generator..."

# Create installation directory if it doesn't exist
if [ ! -d "$INSTALL_DIR" ]; then
    echo "Creating installation directory: $INSTALL_DIR"
    mkdir -p "$INSTALL_DIR"
fi

# Download the binary
echo "Downloading quicklook_generator..."
wget -q --show-progress -O "$INSTALL_DIR/$BINARY_NAME" "$BINARY_URL"

# Make the binary executable
echo "Making binary executable..."
chmod +x "$INSTALL_DIR/$BINARY_NAME"

# Determine shell configuration file
if [[ "$SHELL" == *"/zsh"* ]]; then
    SHELL_CONFIG_FILE="$HOME/.zshrc"
elif [[ "$SHELL" == *"/bash"* ]]; then
    SHELL_CONFIG_FILE="$HOME/.bashrc"
else
    echo "Warning: Unsupported shell detected. You'll need to manually add $INSTALL_DIR to your PATH."
    echo "Add this line to your shell configuration file:"
    echo "export PATH=\"\$PATH:$INSTALL_DIR\""
    exit 1
fi

# Add to PATH if not already present
if ! grep -q "$INSTALL_DIR" "$SHELL_CONFIG_FILE" 2>/dev/null; then
    echo "Adding installation directory to PATH..."
    echo "" >> "$SHELL_CONFIG_FILE"
    echo "# Added by quicklook_generator installer" >> "$SHELL_CONFIG_FILE"
    echo "export PATH=\"\$PATH:$INSTALL_DIR\"" >> "$SHELL_CONFIG_FILE"
    echo "Installation directory added to PATH in $SHELL_CONFIG_FILE"
fi

echo ""
echo "Installation completed successfully!"
echo "To start using quicklook_generator, either:"
echo "1. Start a new terminal session, or"
echo "2. Run: source $SHELL_CONFIG_FILE"
echo ""
echo "Usage example:"
echo "quicklook_generator input.md output.md"
