 #!/bin/bash

# Correct binary download URL from the release assets
BINARY_URL="https://github.com/anegg0/quicklook-generator/releases/download/v1.0.1/quicklook-generator"

BINARY_NAME="quicklook-generator"

INSTALL_DIR="$HOME/.local/bin"

# Ensure the installation directory exists
mkdir -p "$INSTALL_DIR"

# Download the binary using wget
echo "Downloading $BINARY_NAME..."
wget -O "$INSTALL_DIR/$BINARY_NAME" "$BINARY_URL"
if [ $? -ne 0 ]; then
    echo "Error downloading the binary."
    exit 1
fi

# Make the binary executable
chmod +x "$INSTALL_DIR/$BINARY_NAME"

# Determine the shell configuration file based on the user's current shell
if [[ "$SHELL" == *"/zsh"* ]]; then
    SHELL_CONFIG_FILE="$HOME/.zshrc"
elif [[ "$SHELL" == *"/bash"* ]]; then
    SHELL_CONFIG_FILE="$HOME/.bashrc"
else
    echo "Unsupported shell. Please add $INSTALL_DIR to your PATH manually."
    exit 1
fi

# Check if the install directory is in PATH
if [[ ":$PATH:" != *":$INSTALL_DIR:"* ]]; then
    # Provide instructions to add to PATH if not already present
    echo "export PATH=\"\$PATH:$INSTALL_DIR\"" >> "$SHELL_CONFIG_FILE"
    echo "Adding the installation directory to PATH in $SHELL_CONFIG_FILE"
fi

# Inform the user about the update
echo "Installation complete. Please run 'source $SHELL_CONFIG_FILE' or restart your terminal."