#!/bin/bash

# 🚀 AI Governance Architect's Codex - Hugging Face Spaces Deployment Script
# This script deploys the app directly from the deploy_space directory

echo "🧠⚖️ AI Governance Architect's Codex - Hugging Face Spaces Deployment"
echo "=================================================================="

# Check if we're in the right directory
if [ ! -f "app_hf.py" ]; then
    echo "❌ Error: Please run this script from the deploy_space directory"
    echo "   Current directory: $(pwd)"
    echo "   Expected files: app_hf.py, app.py"
    exit 1
fi

echo "✅ Deployment environment verified"
echo "📁 Current directory: $(pwd)"
echo "📋 Files found:"
ls -la *.py | head -5

# Check if gradio is installed
if ! command -v gradio &> /dev/null; then
    echo "❌ Gradio CLI not found. Installing..."
    pip3 install gradio || {
        echo "❌ Failed to install Gradio"
        exit 1
    }
fi

echo "✅ Gradio CLI found"

# Check Python version
PYTHON_VERSION=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
echo "🐍 Python version: $PYTHON_VERSION"

# Install/check dependencies
echo "📦 Checking dependencies..."
pip3 install -q gradio fastapi uvicorn pydantic python-dotenv || {
    echo "⚠️  Some dependencies may be missing, but continuing..."
}

echo ""
echo "🚀 Deploying AI Governance Study Portal to Hugging Face Spaces..."
echo "🌐 Target: https://huggingface.co/spaces/fartec0/ai-governance"
echo "📄 App file: app_hf.py"
echo ""

echo ""
echo "🚀 Deploying AI Governance Study Portal to Hugging Face Spaces..."
echo "🌐 Target: https://huggingface.co/spaces/fartec0/ai-governance"
echo "📄 App file: app_hf.py (with schema patches)"
echo ""

# Deploy using gradio CLI with patched version
echo "📤 Starting deployment with patched app..."
gradio deploy \
    --title "AI Governance Architect's Codex" \
    --app-file app_hf.py || {
    echo ""
    echo "❌ Deployment failed with patched app"
    echo "🔄 Trying safe mode deployment..."
    
    # Alternative: try with safe version
    echo "📄 Trying with app_safe.py (schema-safe version)..."
    gradio deploy \
        --title "AI Governance Architect's Codex - Safe Mode" \
        --app-file app_safe.py || {
        
        echo ""
        echo "🔄 Trying with minimal app.py..."
        gradio deploy \
            --title "AI Governance Architect's Codex" \
            --app-file app.py || {
            
            echo ""
            echo "❌ All deployment methods failed"
            echo "💡 Manual deployment required:"
            echo "   1. Check your Hugging Face token: huggingface-cli login"
            echo "   2. Verify app files are working: python3 app_hf.py"
            echo "   3. Try: gradio deploy --title 'AI Governance Codex' --app-file app_safe.py"
            exit 1
        }
    }
}

echo ""
echo "✅ Deployment completed successfully!"
echo "🌐 Your app should be available at: https://huggingface.co/spaces/fartec0/ai-governance"
echo "⏱️  It may take a few minutes for the space to build and become available"
echo "📝 You can check the build logs in the Hugging Face Spaces interface"
