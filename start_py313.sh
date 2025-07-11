#!/bin/bash

# 🧠⚖️ AI Governance Architect's Codex - Python 3.13 Compatible Launcher
# This script will set up and launch the AI Governance Study Portal
# with Python 3.13 compatible dependencies (PyTorch disabled)

echo "🧠⚖️ AI Governance Architect's Codex (Python 3.13 Compatible)"
echo "============================================================="

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "🐍 Python version: $PYTHON_VERSION"

if [[ "$PYTHON_VERSION" == "3.13" ]]; then
    echo "⚠️  Python 3.13 detected - using PyTorch-free configuration"
    echo "   Some AI features will be limited but core functionality will work"
    REQUIREMENTS_FILE="requirements_py313.txt"
else
    echo "✅ Using standard configuration"
    REQUIREMENTS_FILE="requirements.txt"
fi

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed."
    echo "Please install Python 3.8+ and try again."
    exit 1
fi

echo "✅ Python 3 found"

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed."
    exit 1
fi

echo "✅ pip3 found"

# Install dependencies
echo "📦 Installing dependencies from $REQUIREMENTS_FILE..."
pip3 install -r "$REQUIREMENTS_FILE"

if [ $? -ne 0 ]; then
    echo "❌ Failed to install dependencies"
    echo "💡 Try running: pip3 install --upgrade pip"
    exit 1
fi

echo "✅ Dependencies installed"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p static/images data models temp
echo "✅ Directory structure ready"

# Test components (skip if test file doesn't exist)
if [ -f "test_components.py" ]; then
    echo "🧪 Testing components..."
    python3 test_components.py
    if [ $? -ne 0 ]; then
        echo "⚠️  Some components have issues, but continuing..."
    fi
fi

# Launch the application
echo ""
echo "🚀 Launching AI Governance Study Portal..."
echo "📍 Access at: http://localhost:7860"
echo "⏹️  Press Ctrl+C to stop"

if [[ "$PYTHON_VERSION" == "3.13" ]]; then
    echo "⚠️  Running in Python 3.13 mode - some AI features may be limited"
fi

echo "============================================================="

python3 launch.py
