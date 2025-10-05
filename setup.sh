#!/bin/bash

# Setup script for Ubuntu Voice-to-Text Application

echo "========================================"
echo "Ubuntu Voice-to-Text Setup"
echo "========================================"
echo ""

# Check if running on Ubuntu/Debian
if ! command -v apt &> /dev/null; then
    echo "Error: This script is designed for Ubuntu/Debian systems with apt package manager."
    exit 1
fi

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Found Python $PYTHON_VERSION"

# Install system dependencies
echo ""
echo "Installing system dependencies..."
echo "This requires sudo privileges."
echo ""

PACKAGES="xdotool libportaudio2 portaudio19-dev python3-pip python3-venv libnotify-bin"

echo "The following packages will be installed:"
echo "$PACKAGES"
echo ""
read -p "Continue? (y/n) " -n 1 -r
echo ""

if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Setup cancelled."
    exit 1
fi

sudo apt update
sudo apt install -y $PACKAGES

# Check display server and install appropriate tools
if [ "$XDG_SESSION_TYPE" = "wayland" ]; then
    echo ""
    echo "Wayland detected. Setting up ydotool..."
    
    # Download ydotool and ydotoold if they don't exist
    if [ ! -f "ydotool" ]; then
        echo "Downloading ydotool..."
        wget -q https://github.com/ReimuNotMoe/ydotool/releases/download/v1.0.4/ydotool-release-ubuntu-latest -O ydotool
        chmod +x ydotool
        echo "✓ ydotool downloaded"
    else
        echo "✓ ydotool already exists"
    fi
    
    if [ ! -f "ydotoold" ]; then
        echo "Downloading ydotoold..."
        wget -q https://github.com/ReimuNotMoe/ydotool/releases/download/v1.0.4/ydotoold-release-ubuntu-latest -O ydotoold
        chmod +x ydotoold
        echo "✓ ydotoold downloaded"
    else
        echo "✓ ydotoold already exists"
    fi
    
    # Also install wl-clipboard for clipboard support
    sudo apt install -y wl-clipboard
else
    echo ""
    echo "X11 detected. xdotool is already installed."
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo ""
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo ""
echo "Upgrading pip..."
pip install --upgrade pip

# Install setuptools and wheel (required for building packages)
echo ""
echo "Installing setuptools and wheel..."
pip install --upgrade setuptools wheel

# Install Python dependencies
echo ""
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Make the scripts executable
chmod +x voice_daemon.py voice_trigger.py start_daemon.sh

echo ""
echo "========================================"
echo "Setup Complete!"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. Make sure the Whisper Docker container is running:"
echo "     docker run -d -p 127.0.0.1:4444:4444 --name whisper-assistant whisper-assistant"
echo ""
echo "  2. Start the voice daemon:"
echo "     ./start_daemon.sh"
echo "     (Or setup autostart: ./setup_autostart.sh)"
echo ""
echo "  3. Configure global keyboard shortcut in your desktop environment:"
echo "     Command: $(pwd)/voice_trigger.py"
echo "     Shortcut: Ctrl+Shift+Space (or your preference)"
echo ""
echo "See QUICKSTART.md for detailed instructions!"
echo ""

