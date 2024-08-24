#!/bin/bash

# Function to check if a Python package is installed
check_package() {
    python -c "import $1" 2>/dev/null
    return $?
}

# Check and install requests
if ! check_package requests; then
    echo "Installing requests..."
    paru -S --noconfirm python-requests
fi

# Check and install PyQt5
if ! check_package PyQt5; then
    echo "Installing PyQt5..."
    paru -S --noconfirm python-pyqt5
fi

# Path to your Python script
SCRIPT_PATH="install.py"

# Check if the script exists
if [ ! -f "$SCRIPT_PATH" ]; then
    echo "Error: Cannot find the Python script at $SCRIPT_PATH"
    exit 1
fi

# Start the Python script
echo "Starting the installation tool..."
python "$SCRIPT_PATH"