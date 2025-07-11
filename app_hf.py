#!/usr/bin/env python3
"""
🧠⚖️ AI Governance Architect's Codex - Hugging Face Space Launcher
Simplified launcher for Hugging Face Spaces deployment
"""

import os
from pathlib import Path
from app import create_main_interface

# Create necessary directories
def setup_directories():
    """Create necessary directories if they don't exist"""
    directories = ['static/images', 'data', 'models', 'temp']
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    print("✅ Directory structure ready")

# Setup environment
print("🧠⚖️ AI Governance Architect's Codex")
print("=" * 60)

# Create necessary directories
setup_directories()

# Create and launch the interface
print("🚀 Initializing application...")
app = create_main_interface()

# Mount the app for local development with share link
print("📍 Launching with public share link...")
app.launch(
    share=True,  # Enable share link for external access
    server_name="0.0.0.0",  # Listen on all interfaces
    server_port=7860,  # Use port 7860
    show_api=True,  # Show API docs
    show_error=True,  # Show detailed errors
    favicon_path="static/images/favicon.ico"  # Custom favicon
) 