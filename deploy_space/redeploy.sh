#!/bin/bash

echo "🚀 Redeploying AI Governance Architect's Codex to Hugging Face Spaces..."
echo "=================================================="

# Check if we're in the right directory
if [ ! -f "app_hf.py" ]; then
    echo "❌ Error: Please run this script from the deploy_space directory"
    exit 1
fi

echo "📦 Updating files..."

# Add all files to git (if git is initialized)
if [ -d ".git" ]; then
    git add .
    git commit -m "Fix Gradio compatibility issues and update requirements"
    git push
    echo "✅ Changes pushed to repository"
else
    echo "ℹ️  No git repository found - please manually update your Hugging Face Space"
fi

echo "=================================================="
echo "✅ Redeploy complete!"
echo "🌐 Check your Space at: https://huggingface.co/spaces/fartec0/ai-governance"
echo "⏱️  It may take a few minutes for changes to take effect"
