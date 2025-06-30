#!/bin/bash

# 🧠⚖️ AI Governance Architect's Codex - Easy Launcher
# This script will set up and launch the AI Governance Study Portal

echo "🧠⚖️ AI Governance Architect's Codex"
echo "===================================="

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

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "📦 Installing dependencies..."
    pip3 install -r requirements.txt
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install dependencies"
        exit 1
    fi
    echo "✅ Dependencies installed"
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p static/images data models temp
echo "✅ Directory structure ready"

# Test components
echo "🧪 Testing components..."
python3 test_components.py
if [ $? -ne 0 ]; then
    echo "⚠️  Some components have issues, but continuing..."
fi

# Launch the application
echo ""
echo "🚀 Launching AI Governance Study Portal..."
echo "📍 Access at: http://localhost:7860"
echo "⏹️  Press Ctrl+C to stop"
echo "===================================="

python3 launch.py 