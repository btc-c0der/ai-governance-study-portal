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

# Function to install PyTorch
install_pytorch() {
    echo "🔥 Installing PyTorch..."
    
    # Try CPU version first (most compatible)
    echo "Trying CPU-only PyTorch installation..."
    pip3 install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu
    
    if [ $? -eq 0 ]; then
        echo "✅ PyTorch (CPU) installed successfully"
        return 0
    fi
    
    # Fall back to regular PyTorch
    echo "Trying regular PyTorch installation..."
    pip3 install torch torchvision torchaudio
    
    if [ $? -eq 0 ]; then
        echo "✅ PyTorch installed successfully"
        return 0
    fi
    
    echo "❌ Failed to install PyTorch"
    return 1
}

# Create a minimal requirements file without torch
create_minimal_requirements() {
    echo "📝 Creating minimal requirements without PyTorch..."
    cat > requirements_minimal.txt << 'EOF'
# Core Framework
gradio>=4.15.0
fastapi>=0.104.0
uvicorn>=0.24.0

# Data & Visualization
pandas>=2.0.3
numpy>=1.24.3
plotly>=5.17.0
matplotlib>=3.8.0
seaborn>=0.13.0

# Web & API
requests>=2.31.0
httpx>=0.25.0
pydantic>=2.5.0

# Database & Storage
tinydb>=4.8.0

# EU AI Act & Legal Data Processing
beautifulsoup4>=4.12.2
lxml>=4.9.0
pypdf2>=3.0.0
python-docx>=1.1.0

# Auth & Security
python-jose>=3.3.0
passlib>=1.7.0
python-multipart>=0.0.6

# Utilities
python-dotenv>=1.0.0
typing-extensions>=4.8.0

# Development
pytest>=7.4.0
black>=23.0.0
flake8>=6.0.0
markdown>=3.4.3
EOF
}

# Install dependencies
echo "📦 Installing dependencies..."

# First, try to install PyTorch
if install_pytorch; then
    # PyTorch installed successfully, now install full requirements
    echo "📦 Installing full requirements..."
    pip3 install -r requirements.txt
    
    if [ $? -ne 0 ]; then
        echo "⚠️  Some dependencies failed to install, trying minimal setup..."
        create_minimal_requirements
        pip3 install -r requirements_minimal.txt
        
        if [ $? -ne 0 ]; then
            echo "❌ Failed to install minimal dependencies"
            exit 1
        fi
        echo "✅ Minimal dependencies installed (some AI features may be limited)"
    else
        echo "✅ All dependencies installed successfully"
    fi
else
    # PyTorch failed, try minimal requirements
    echo "⚠️  PyTorch installation failed, installing minimal requirements..."
    create_minimal_requirements
    pip3 install -r requirements_minimal.txt
    
    if [ $? -ne 0 ]; then
        echo "❌ Failed to install minimal dependencies"
        exit 1
    fi
    echo "✅ Minimal dependencies installed (AI features will be limited)"
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
