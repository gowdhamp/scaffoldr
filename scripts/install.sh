#!/bin/bash

set -e

# Detect OS and Architecture
OS=$(uname -s | tr '[:upper:]' '[:lower:]')
ARCH=$(uname -m)

if [ "$ARCH" = "x86_64" ]; then
    ARCH="x86_64"
elif [ "$ARCH" = "aarch64" ] || [ "$ARCH" = "arm64" ]; then
    ARCH="arm64"
else
    echo "Unsupported architecture: $ARCH"
    exit 1
fi

if [ "$OS" = "darwin" ]; then
    OS="darwin"
elif [ "$OS" = "linux" ]; then
    OS="linux"
else
    echo "Unsupported OS: $OS"
    exit 1
fi

BINARY_NAME="scaffoldr-${OS}-${ARCH}"

URL="https://github.com/gowdhamp/scaffoldr/releases/latest/download/${BINARY_NAME}"
INSTALL_DIR="/usr/local/bin"
TARGET="${INSTALL_DIR}/scaffoldr"

echo "Downloading Scaffoldr for ${OS} ${ARCH}..."
curl -L "$URL" -o scaffoldr_tmp

echo "Installing to ${TARGET}..."
sudo mv scaffoldr_tmp "$TARGET"
sudo chmod +x "$TARGET"

echo "Scaffoldr installed successfully!"
scaffoldr --help
