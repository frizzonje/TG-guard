#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# Print colored message
print_message() {
    COLOR=$1
    MSG=$2
    echo -e "${COLOR}${MSG}${NC}"
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Main header
print_message "${GREEN}" "
🤖 TG-Guard - Installation Script
================================="

# Check Python version
print_message "${YELLOW}" "\n📋 Checking Python version..."
if ! command_exists python3; then
    print_message "${RED}" "❌ Python 3 is not installed. Please install Python 3.7 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
if (( $(echo "$PYTHON_VERSION < 3.7" | bc -l) )); then
    print_message "${RED}" "❌ Python version must be 3.7 or higher. Found version: $PYTHON_VERSION"
    exit 1
fi
print_message "${GREEN}" "✅ Python version $PYTHON_VERSION detected"

# Check if virtual environment exists
VENV_DIR=".venv"
if [ -d "$VENV_DIR" ]; then
    print_message "${YELLOW}" "\n🔄 Virtual environment already exists. Do you want to recreate it? [y/N]"
    read -r response
    if [[ "$response" =~ ^([yY][eE][sS]|[yY])+$ ]]; then
        print_message "${YELLOW}" "🗑️ Removing existing virtual environment..."
        rm -rf "$VENV_DIR"
    else
        print_message "${GREEN}" "✅ Using existing virtual environment"
    fi
fi

# Create virtual environment if it doesn't exist
if [ ! -d "$VENV_DIR" ]; then
    print_message "${YELLOW}" "\n📦 Creating virtual environment..."
    if ! python3 -m venv "$VENV_DIR"; then
        print_message "${RED}" "❌ Failed to create virtual environment"
        exit 1
    fi
    print_message "${GREEN}" "✅ Virtual environment created"
fi

# Activate virtual environment
print_message "${YELLOW}" "\n🔄 Activating virtual environment..."
source "$VENV_DIR/bin/activate"

# Upgrade pip
print_message "${YELLOW}" "\n🔄 Upgrading pip..."
pip install --upgrade pip

# Install requirements
print_message "${YELLOW}" "\n📦 Installing dependencies..."
if ! pip install -r requirements.txt; then
    print_message "${RED}" "❌ Failed to install dependencies"
    exit 1
fi

# Check if .env exists
if [ ! -f ".env" ]; then
    print_message "${YELLOW}" "\n📝 Creating .env file..."
    print_message "${BOLD}" "\nPlease enter your Telegram API credentials:"
    
    echo -n "Enter your API ID: "
    read -r API_ID
    
    echo -n "Enter your API Hash: "
    read -r API_HASH
    
    echo -n "Enter session name (default: my_user_session): "
    read -r SESSION_NAME
    SESSION_NAME=${SESSION_NAME:-my_user_session}
    
    # Create .env file
    cat > .env << EOL
API_ID = $API_ID
API_HASH = "$API_HASH"
SESSION = "$SESSION_NAME"
EOL
    
    print_message "${GREEN}" "✅ .env file created"
else
    print_message "${GREEN}" "✅ .env file already exists"
fi

# Success message
print_message "${GREEN}" "\n✅ Installation completed successfully!"
print_message "${YELLOW}" "\nTo run TG-Guard:
1. Make sure you're in the virtual environment:
   source .venv/bin/activate
2. Run the script:
   python main.py

❗ Note: Make sure to configure your settings in config.py before running the script."