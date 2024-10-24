#!/bin/bash

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Check if Python is installed
if ! command_exists python3; then
    echo "Python 3 is not installed. Please install Python 3 and try again."
    exit 1
fi

# Check if pip is installed
if ! command_exists pip3; then
    echo "pip3 is not installed. Please install pip3 and try again."
    exit 1
fi

# Check if OpenRGB is installed
if ! command_exists openrgb; then
    echo "OpenRGB is not installed. Attempting to install..."
    sudo pacman -S openrgb
    if [ $? -ne 0 ]; then
        echo "Failed to install OpenRGB. Please install it manually and try again."
        exit 1
    fi
fi

# Check if virtual environment exists, if not create it
if [ ! -d "rgb" ]; then
    echo "Creating virtual environment..."
    python3 -m venv rgb
fi

# Activate virtual environment
source rgb/bin/activate

# Install or upgrade required packages
echo "Installing/upgrading required packages..."
pip install --upgrade pip
pip install --upgrade PyQt5 openrgb-python

# Run the RAM LED controller
echo "Starting RAM LED Controller..."
python3 rgbctrl.py

# Deactivate virtual environment
deactivate
