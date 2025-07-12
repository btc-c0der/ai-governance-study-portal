#!/usr/bin/env python3
"""
🧪 Test script to verify the app works before deployment
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_app_creation():
    """Test if the app can be created without errors"""
    try:
        print("🧪 Testing app creation...")
        
        # Test minimal interface
        from app_hf import create_main_interface
        app = create_main_interface()
        
        print("✅ App creation successful")
        print(f"📊 App type: {type(app)}")
        return True
        
    except Exception as e:
        print(f"❌ App creation failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_imports():
    """Test if all required modules can be imported"""
    try:
        print("🧪 Testing imports...")
        
        import gradio as gr
        print(f"✅ Gradio version: {gr.__version__}")
        
        import fastapi
        print(f"✅ FastAPI version: {fastapi.__version__}")
        
        import pydantic
        print(f"✅ Pydantic version: {pydantic.__version__}")
        
        return True
        
    except Exception as e:
        print(f"❌ Import test failed: {e}")
        return False

if __name__ == "__main__":
    print("🧠⚖️ AI Governance Codex - Pre-deployment Test")
    print("=" * 50)
    
    success = True
    
    # Test imports
    if not test_imports():
        success = False
    
    print()
    
    # Test app creation
    if not test_app_creation():
        success = False
    
    print()
    
    if success:
        print("✅ All tests passed! Ready for deployment.")
        sys.exit(0)
    else:
        print("❌ Some tests failed. Please check the errors above.")
        sys.exit(1)
