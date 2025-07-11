#!/usr/bin/env python3
"""
🧠⚖️ AI Governance Architect's Codex - Hugging Face Space Launcher
Simplified launcher for Hugging Face Spaces deployment
"""

from app import create_main_interface

# Create and launch the interface
app = create_main_interface()

# Mount the app for Hugging Face Spaces
app.launch(
    share=True,  # Enable share link for external access
    server_name="0.0.0.0",  # Listen on all interfaces
    server_port=7861,  # Use alternative port
    show_api=True,  # Show API docs
    show_error=True,  # Show detailed errors
    favicon_path="static/images/favicon.ico"  # Custom favicon
) 