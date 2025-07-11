#!/usr/bin/env python3
"""
Project Structure Validation Script
Validates that the project reorganization was successful
"""

import os
import sys
from pathlib import Path

def validate_structure():
    """Validate the project structure"""
    
    print("🔍 Validating project structure...")
    
    # Define expected structure
    expected_structure = {
        'tests': [
            'test_auth_comprehensive.py',
            'test_complete_auth.py',
            'test_registration_ui.py',
            'test_notes_functionality.py',
            'run_tests.py',
            '__init__.py'
        ],
        'scripts': [
            'start.sh',
            'deploy.py',
            'launch.py',
            'celebration.py',
            'debug_torch.sh'
        ],
        'docs': [
            'AUTHENTICATION_IMPLEMENTATION_COMPLETE.md',
            'README.md',
            'DEPLOYMENT_GUIDE.md',
            'EU_AI_ACT_INTEGRATION_COMPLETE.md'
        ],
        'components': [
            'auth_manager.py',
            'curriculum.py',
            'ai_act_explorer.py',
            'model_demos.py'
        ]
    }
    
    # Check root files
    root_files = ['app.py', 'README.md', 'requirements.txt']
    
    print("\n📁 Checking root files...")
    for file in root_files:
        if Path(file).exists():
            print(f"✅ {file}")
        else:
            print(f"❌ {file} - Missing")
    
    # Check folders and their contents
    for folder, files in expected_structure.items():
        print(f"\n📁 Checking {folder}/ folder...")
        
        if not Path(folder).exists():
            print(f"❌ {folder}/ folder does not exist")
            continue
        
        print(f"✅ {folder}/ folder exists")
        
        # Check some key files in each folder
        for file in files[:3]:  # Check first 3 files
            file_path = Path(folder) / file
            if file_path.exists():
                print(f"  ✅ {file}")
            else:
                print(f"  ❌ {file} - Missing")
    
    # Test imports
    print(f"\n🔧 Testing imports...")
    try:
        sys.path.append('.')
        from components.auth_manager import AuthManager
        print("✅ Components import successfully")
    except ImportError as e:
        print(f"❌ Components import failed: {e}")
    
    # Check test structure
    print(f"\n🧪 Testing test structure...")
    try:
        sys.path.append('tests')
        # This should work if the path updates were successful
        test_path = Path('tests/test_auth_comprehensive.py')
        if test_path.exists():
            print("✅ Test files exist in tests/ folder")
        else:
            print("❌ Test files missing from tests/ folder")
    except Exception as e:
        print(f"❌ Test structure check failed: {e}")
    
    print(f"\n🎉 Structure validation complete!")

if __name__ == "__main__":
    validate_structure()
