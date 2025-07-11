#!/usr/bin/env python3
"""
🧠⚖️ AI Governance Architect's Codex - Hugging Face Space Launcher
Simplified launcher for Hugging Face Spaces deployment
"""

import os
import sys
from pathlib import Path

# Add current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from app import create_main_interface
except ImportError as e:
    print(f"Import error: {e}")
    print("Creating fallback interface...")
    
    import gradio as gr
    
    def create_main_interface():
        """Fallback interface if main app fails to import"""
        with gr.Blocks(title="AI Governance Codex") as app:
            gr.HTML("""
            <div style="text-align: center; padding: 2rem;">
                <h1>🧠⚖️ AI Governance Architect's Codex</h1>
                <p>Loading application components...</p>
                <p>If this message persists, please check the logs for import errors.</p>
            </div>
            """)
        return app

# Create necessary directories for Hugging Face Spaces
def setup_directories():
    """Create necessary directories if they don't exist"""
    directories = ['static/images', 'data', 'models', 'temp']
    for dir_path in directories:
        Path(dir_path).mkdir(parents=True, exist_ok=True)
    print("✅ Directory structure ready")

# Setup environment
print("🧠⚖️ AI Governance Architect's Codex - Hugging Face Spaces")
print("=" * 60)

# Create necessary directories
setup_directories()

# Create and launch the interface
print("🚀 Initializing application...")
try:
    app = create_main_interface()
    print("✅ Application initialized successfully")
except Exception as e:
    print(f"❌ App creation error: {e}")
    import gradio as gr
    
    with gr.Blocks(title="AI Governance Codex - Error") as app:
        gr.HTML(f"""
        <div style="text-align: center; padding: 2rem; background: #fee2e2; border-radius: 10px;">
            <h1>🧠⚖️ AI Governance Architect's Codex</h1>
            <h2>⚠️ Initialization Error</h2>
            <p><strong>Error:</strong> {str(e)}</p>
            <p>Please check the Spaces logs for detailed error information.</p>
        </div>
        """)

# Mount the app for Hugging Face Spaces
print("📍 Launching on Hugging Face Spaces...")
try:
    app.launch(
        share=False,  # No need for share link in Spaces
        server_name="0.0.0.0",  # Listen on all interfaces
        server_port=7860,  # Default Spaces port
        show_error=True,  # Show errors for debugging
        quiet=False  # Show startup messages
    )
except Exception as e:
    print(f"❌ Launch error: {e}")
    # Fallback launch with minimal config
    try:
        app.launch(server_port=7860)
    except Exception as fallback_error:
        print(f"❌ Fallback launch also failed: {fallback_error}")
        print("Check logs for detailed error information.") 