#!/usr/bin/env python3
"""
🎓 AI Governance PhD Study Portal Launcher
Secure authentication-enabled launcher for the academic study portal
"""

import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'gradio>=4.0.0',
        'sqlite3',
        'hashlib',
        'secrets',
        'pandas',
        'plotly',
        'pathlib'
    ]
    
    print("🔍 Checking dependencies...")
    
    missing_packages = []
    for package in required_packages:
        try:
            if '=' in package:
                package_name = package.split('>=')[0]
            else:
                package_name = package
            
            __import__(package_name)
            print(f"✅ {package_name}")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package_name}")
    
    if missing_packages:
        print(f"\n⚠️  Missing packages: {', '.join(missing_packages)}")
        install = input("Install missing packages? (y/n): ")
        if install.lower() == 'y':
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
        else:
            print("❌ Cannot proceed without required packages")
            sys.exit(1)
    
    print("✅ All dependencies satisfied!")

def setup_data_directory():
    """Create data directory if it doesn't exist"""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    print(f"📁 Data directory ready: {data_dir.absolute()}")

def display_welcome():
    """Display welcome message"""
    welcome_banner = """
    ╔═══════════════════════════════════════════════════════════════════════════════════╗
    ║                                                                                   ║
    ║     🎓 AI Governance Architect's Codex - PhD Study Portal                        ║
    ║                                                                                   ║
    ║     🔐 Authentication-Enabled Academic Portal                                     ║
    ║                                                                                   ║
    ║     Features:                                                                     ║
    ║     • 🔐 Secure user authentication & registration                                ║
    ║     • 👑 Admin panel for user management                                          ║
    ║     • 📖 Protected curriculum tracking                                            ║
    ║     • ⚖️  EU AI Act explorer with progress tracking                              ║
    ║     • 🤖 Interactive ML model demonstrations                                     ║
    ║     • 🧠 Personalized AI tutor                                                   ║
    ║     • 📊 Individual performance analytics                                        ║
    ║     • 🧪 Mock AIGP certification exams                                           ║
    ║                                                                                   ║
    ║     👑 Default Admin: fartec0@protonmail.com                                      ║
    ║     🔑 Initial Password: fartec0@protonmail.com                                   ║
    ║                                                                                   ║
    ╚═══════════════════════════════════════════════════════════════════════════════════╝
    """
    print(welcome_banner)

def main():
    """Main launcher function"""
    try:
        # Display welcome
        display_welcome()
        
        # Check dependencies
        check_dependencies()
        
        # Setup data directory
        setup_data_directory()
        
        # Launch the app
        print("\n🚀 Launching AI Governance PhD Study Portal...")
        print("📍 The portal will be available at: http://localhost:7860")
        print("🌐 Public URL will be generated automatically")
        print("\n🎯 Getting Started:")
        print("   1. Go to the 🔐 Authentication tab")
        print("   2. Login with admin credentials or register as new student")
        print("   3. Access your protected 🎓 Student Portal")
        print("   4. Start your AI governance journey!")
        print("\n⚠️  IMPORTANT: Change the default admin password after first login!")
        print("\n" + "="*80)
        
        # Import and run the app
        from app import create_main_interface
        
        app = create_main_interface()
        app.launch(
            server_name="0.0.0.0",
            server_port=7860,
            share=True,
            show_error=True,
            debug=False  # Set to False for production
        )
        
    except KeyboardInterrupt:
        print("\n\n👋 Goodbye! Thanks for using AI Governance Architect's Codex!")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error launching portal: {e}")
        print("💡 Try running: python3 app.py directly")
        sys.exit(1)

if __name__ == "__main__":
    main() 