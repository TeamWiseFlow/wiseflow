#!/bin/bash

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
print_info() {
    echo -e "${GREEN}✅ [INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}⚠️  [WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}❌ [ERROR]${NC} $1"
}

# Check if uv is installed
if ! command -v uv &> /dev/null; then
    print_error "uv is not installed. Please install uv first:"
    echo "  curl -LsSf https://astral.sh/uv/install.sh | sh"
    echo "  Or visit: https://docs.astral.sh/uv/getting-started/installation/"
    exit 1
fi

# Sync dependencies using uv
print_info "Syncing dependencies with uv..."
if ! uv sync; then
    print_error "Failed to sync dependencies with uv"
    exit 1
fi

# Check if we're already in a virtual environment
if [[ "$VIRTUAL_ENV" != "" ]]; then
    print_info "Already in virtual environment: $VIRTUAL_ENV"
else
    # Check if .venv exists
    if [ -d ".venv" ]; then
        print_info "Activating virtual environment..."
        source .venv/bin/activate
        if [[ "$VIRTUAL_ENV" != "" ]]; then
            print_info "Virtual environment activated: $VIRTUAL_ENV"
        else
            print_error "Failed to activate virtual environment"
            exit 1
        fi
    else
        print_warning "No .venv directory found. Running uv sync should have created it."
        print_info "Trying to activate virtual environment..."
        source .venv/bin/activate 2>/dev/null || {
            print_error "Could not activate virtual environment. Please run 'uv sync' manually."
            exit 1
        }
    fi
fi

# Check and start PocketBase
# First check if port 8090 is in use
if netstat -tuln 2>/dev/null | grep ":8090" > /dev/null || lsof -i :8090 2>/dev/null > /dev/null; then
    print_info "Port 8090 is already in use, checking if it's PocketBase..."
    
    # Check if it's actually pocketbase using the port
    if pgrep -f "pocketbase.*serve" > /dev/null || pgrep -f "./pb/pocketbase" > /dev/null; then
        print_info "PocketBase is already running."
    else
        print_warning "Port 8090 is in use by another process. Please stop it first or use a different port."
    fi
else
    # Port is available, check if pocketbase process exists anyway
    if pgrep -f "pocketbase.*serve" > /dev/null || pgrep -f "./pb/pocketbase" > /dev/null; then
        print_warning "PocketBase process found but not using port 8090. It might have crashed."
        print_info "Attempting to start PocketBase on port 8090..."
    else
        print_info "Starting PocketBase..."
    fi
    
    # Start PocketBase
    ./pb/pocketbase serve --http=127.0.0.1:8090 &
    
    # Give it a moment to start and check if it's running
    sleep 2
    if netstat -tuln 2>/dev/null | grep ":8090" > /dev/null || lsof -i :8090 2>/dev/null > /dev/null; then
        print_info "PocketBase started successfully on port 8090."
    else
        print_error "Failed to start PocketBase. Please check for errors."
    fi
fi

# Run the main application
print_info "Starting WiseFlow application..."
python core/run_task.py