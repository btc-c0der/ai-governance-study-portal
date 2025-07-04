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
    share=False,  # No need for share link in Spaces
    server_name="0.0.0.0",  # Listen on all interfaces
    server_port=7860,  # Default Spaces port
    show_api=True,  # Hide API docs for production
    show_error=True,  # Hide detailed errors in production
    favicon_path="static/images/favicon.ico"  # Custom favicon
) 