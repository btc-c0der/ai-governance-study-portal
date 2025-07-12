#!/bin/bash

# 🧠⚖️ AI Governance Architect's Codex - Easy Launcher
# This script will set up and launch the AI Governance Study Portal

echo "🧠⚖️ AI Governance Architect's Codex"
echo "===================================="

# Check Python version and compatibility
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "🐍 Python version: $PYTHON_VERSION"

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

# Determine which requirements file to use
if [[ "$PYTHON_VERSION" == "3.13" ]]; then
    echo "⚠️  Python 3.13 detected - using PyTorch-free configuration"
    echo "   Some AI features will be limited but core functionality will work"
    
    if [ -f "requirements_py313.txt" ]; then
        REQUIREMENTS_FILE="requirements_py313.txt"
    else
        echo "📝 Creating Python 3.13 compatible requirements..."
        cat > requirements_py313.txt << 'EOF'
# Core Framework - Python 3.13 Compatible
gradio>=4.15.0
fastapi>=0.104.0
uvicorn>=0.24.0
scikit-learn>=1.3.0
pandas>=2.0.3
numpy>=1.24.3
plotly>=5.17.0
matplotlib>=3.8.0
seaborn>=0.13.0
requests>=2.31.0
httpx>=0.25.0
pydantic>=2.5.0
tinydb>=4.8.0
beautifulsoup4>=4.12.2
lxml>=4.9.0
pypdf2>=3.0.0
python-docx>=1.1.0
python-jose>=3.3.0
passlib>=1.7.0
python-multipart>=0.0.6
python-dotenv>=1.0.0
typing-extensions>=4.8.0
markdown>=3.4.3
EOF
        REQUIREMENTS_FILE="requirements_py313.txt"
    fi
else
    echo "✅ Using standard configuration"
    REQUIREMENTS_FILE="requirements.txt"
fi

# Install dependencies
echo "📦 Installing dependencies from $REQUIREMENTS_FILE..."

# Try to install dependencies, but continue even if some fail
pip3 install -r "$REQUIREMENTS_FILE" || {
    echo "⚠️  Some dependencies failed to install. Trying alternative approach..."
    
    # Install core dependencies that should work
    pip3 install gradio fastapi uvicorn pandas numpy plotly matplotlib requests pydantic python-dotenv || {
        echo "❌ Failed to install core dependencies"
        exit 1
    }
    
    echo "✅ Core dependencies installed (some features may be limited)"
}

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p static/images data models temp
echo "✅ Directory structure ready"

# Test components
echo "🧪 Testing components..."
python3 tests/test_components.py
if [ $? -ne 0 ]; then
    echo "⚠️  Some components have issues, but continuing..."
fi

# Check for deployment argument
if [ "$1" == "deploy" ]; then
    echo ""
    echo "🚀 Deploying AI Governance Study Portal to Hugging Face Spaces..."
    echo "=================================================="
    
    # Check if gradio is installed
    if ! command -v gradio &> /dev/null; then
        echo "❌ Gradio CLI not found. Installing..."
        pip3 install gradio[deploy] || {
            echo "❌ Failed to install Gradio deployment tools"
            exit 1
        }
    fi
    
    # Check if deploy_space directory exists
    if [ ! -d "deploy_space" ]; then
        echo "❌ deploy_space directory not found"
        exit 1
    fi
    
    # Use the dedicated deployment script
    echo "📦 Using dedicated deployment script..."
    cd deploy_space && ./deploy.sh
    
    # Check if deployment was successful
    if [ $? -eq 0 ]; then
        echo "✅ Deployment completed successfully!"
        echo "🌐 Access your space at: https://huggingface.co/spaces/fartec0/ai-governance"
    else
        echo "❌ Deployment failed"
        echo "💡 You can also try manual deployment:"
        echo "   cd deploy_space && ./deploy.sh"
        exit 1
    fi
    
elif [ "$1" == "test" ]; then
    echo ""
    echo "🧪 Testing AI Governance Study Portal locally..."
    echo "📍 Access at: http://localhost:7860"
    echo "⏹️  Press Ctrl+C to stop"
    echo "===================================="
    
    python3 app_hf.py
    
else
    echo ""
    echo "🚀 Launching AI Governance Study Portal..."
    echo "📍 Local development server: http://localhost:7860"
    echo "⏹️  Press Ctrl+C to stop"
    echo ""
    echo "💡 Usage options:"
    echo "   ./start.sh        - Run locally"
    echo "   ./start.sh test   - Test locally"
    echo "   ./start.sh deploy - Deploy to Hugging Face Spaces"
    echo "===================================="
    
    python3 app_hf.py 
fi 