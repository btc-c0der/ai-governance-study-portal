#!/usr/bin/env python3
"""
🚀 AI Governance Codex Launcher
Simple launcher with dependency checking and user-friendly error messages.
"""

import sys
import subprocess
import importlib
import os

def check_python_version():
    """Check if Python version is compatible"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required. Current version:", sys.version)
        return False
    print(f"✅ Python {sys.version.split()[0]} detected")
    return True

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'gradio',
        'pandas',
        'plotly',
        'scikit-learn',
        'numpy'
    ]
    
    missing_packages = []
    
    for package in required_packages:
        try:
            importlib.import_module(package)
            print(f"✅ {package} installed")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} not found")
    
    if missing_packages:
        print(f"\n📦 Installing missing packages: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install"] + missing_packages
            )
            print("✅ Dependencies installed successfully!")
            return True
        except subprocess.CalledProcessError:
            print("❌ Failed to install dependencies. Please run:")
            print(f"pip install {' '.join(missing_packages)}")
            return False
    
    return True

def create_directories():
    """Create required directories"""
    dirs = ['static/images', 'data', 'models', 'temp']
    for dir_path in dirs:
        os.makedirs(dir_path, exist_ok=True)
    print("✅ Directory structure created")

def main():
    """Main launcher function"""
    print("🧠⚖️ AI Governance Architect's Codex Launcher")
    print("=" * 50)
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    # Check and install dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Create directories
    create_directories()
    
    # Import and launch the app
    try:
        print("\n🚀 Launching AI Governance Study Portal...")
        print("📍 Access the portal at: http://localhost:7860")
        print("🔄 The app will open in your default browser")
        print("⏹️  Press Ctrl+C to stop the server")
        print("=" * 50)
        
        from app import create_main_interface
        app = create_main_interface()
        app.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=False,  # Set to True for public sharing
            debug=False,
            show_error=True,
            inbrowser=True  # Automatically open browser
        )
        
    except KeyboardInterrupt:
        print("\n👋 Thank you for using AI Governance Codex!")
        print("EU LAW WILL BE LAWFUL AND AI WILL BE GBU2 LICENSED 🤖⚖️")
        
    except Exception as e:
        print(f"\n❌ Error launching application: {e}")
        print("💡 Try running: python app.py")
        sys.exit(1)

if __name__ == "__main__":
    main() 