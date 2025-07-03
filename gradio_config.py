#!/usr/bin/env python3
"""
Gradio Deployment Configuration
Handles SSE and deployment settings for better compatibility
"""

import os
import gradio as gr
from pathlib import Path

# Deployment settings
DEPLOYMENT_CONFIG = {
    # SSE Configuration
    "enable_sse": True,
    "sse_heartbeat": 30,
    
    # Server settings
    "server_name": "0.0.0.0",
    "server_port": 7860,
    "share": False,
    "debug": False,
    "show_error": True,
    "show_tips": False,
    
    # Performance settings
    "max_threads": 40,
    "concurrency_count": 5,
    
    # File upload limits
    "max_file_size": "10mb",
    
    # CORS settings for deployment
    "allow_origins": ["*"],
    "allow_methods": ["GET", "POST"],
    "allow_headers": ["*"],
}

def get_deployment_config():
    """Get deployment configuration based on environment"""
    
    # Check if running on Hugging Face Spaces
    if os.getenv("SPACE_ID"):
        config = DEPLOYMENT_CONFIG.copy()
        config.update({
            "server_name": "0.0.0.0",
            "server_port": 7860,
            "share": False,  # Don't use share on Spaces
            "enable_queue": True,
            "favicon_path": None,
        })
        return config
    
    # Local development configuration
    else:
        config = DEPLOYMENT_CONFIG.copy()
        config.update({
            "inbrowser": True,
            "favicon_path": None,
        })
        return config

def create_gradio_app_with_config(interface_fn):
    """Create Gradio app with proper configuration"""
    
    config = get_deployment_config()
    
    # Create the interface
    app = interface_fn()
    
    return app, config

def deploy_with_retry(app, config, max_retries=3):
    """Deploy with retry logic for SSE issues"""
    
    for attempt in range(max_retries):
        try:
            print(f"🚀 Deployment attempt {attempt + 1}/{max_retries}")
            
            # Launch with configuration
            app.launch(**config)
            break
            
        except Exception as e:
            print(f"❌ Deployment attempt {attempt + 1} failed: {e}")
            
            if attempt < max_retries - 1:
                print("⏳ Retrying in 5 seconds...")
                import time
                time.sleep(5)
            else:
                print("💥 All deployment attempts failed!")
                raise e 