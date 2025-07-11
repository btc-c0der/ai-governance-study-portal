#!/bin/bash

# Debug script to test PyTorch installation options

echo "🔧 PyTorch Installation Debug Script"
echo "====================================="

# Test 1: Regular PyTorch installation
echo "Test 1: Regular PyTorch installation"
pip3 install torch --dry-run --quiet 2>&1 | head -5

# Test 2: CPU-only PyTorch installation  
echo ""
echo "Test 2: CPU-only PyTorch installation"
pip3 install torch --index-url https://download.pytorch.org/whl/cpu --dry-run --quiet 2>&1 | head -5

# Test 3: Check if torch is already installed
echo ""
echo "Test 3: Check current torch installation"
python3 -c "import torch; print(f'PyTorch version: {torch.__version__}')" 2>/dev/null || echo "PyTorch not installed"

# Test 4: Check Python version and architecture
echo ""
echo "Test 4: System information"
python3 -c "import sys; print(f'Python version: {sys.version}')"
python3 -c "import platform; print(f'Platform: {platform.platform()}')"
python3 -c "import platform; print(f'Architecture: {platform.architecture()}')"

echo ""
echo "====================================="
echo "🔧 Debug complete"
