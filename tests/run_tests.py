#!/usr/bin/env python3
"""
Test Runner for AI Governance Architect's Codex

Usage:
    python run_tests.py              # Run all tests
    python run_tests.py auth         # Run authentication tests
    python run_tests.py notes        # Run notes functionality tests
    python run_tests.py ui           # Run UI tests
"""

import subprocess
import sys
import os
from pathlib import Path

def run_test(test_file):
    """Run a single test file"""
    print(f"\n{'='*60}")
    print(f"🧪 Running {test_file}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run([sys.executable, test_file], 
                              capture_output=True, text=True, cwd=Path(__file__).parent)
        
        if result.returncode == 0:
            print(f"✅ {test_file} PASSED")
            print(result.stdout)
        else:
            print(f"❌ {test_file} FAILED")
            print(result.stdout)
            print(result.stderr)
        
        return result.returncode == 0
    
    except Exception as e:
        print(f"❌ Error running {test_file}: {e}")
        return False

def main():
    """Main test runner"""
    test_dir = Path(__file__).parent
    
    # Define test categories
    test_categories = {
        'auth': [
            'test_auth_comprehensive.py',
            'test_complete_auth.py', 
            'test_registration_ui.py'
        ],
        'notes': [
            'test_notes_functionality.py'
        ],
        'ui': [
            'test_registration_ui.py',
            'test_simple_features.py'
        ],
        'all': [
            'test_auth_comprehensive.py',
            'test_complete_auth.py',
            'test_registration_ui.py',
            'test_notes_functionality.py',
            'test_simple_features.py',
            'test_progress_tracking.py',
            'test_final_features.py',
            'test_content.py',
            'test_charts.py'
        ]
    }
    
    category = sys.argv[1] if len(sys.argv) > 1 else 'all'
    
    if category not in test_categories:
        print(f"❌ Unknown test category: {category}")
        print(f"Available categories: {', '.join(test_categories.keys())}")
        return
    
    tests_to_run = test_categories[category]
    
    print(f"🚀 Starting test suite for category: {category}")
    print(f"📋 Tests to run: {len(tests_to_run)}")
    
    passed = 0
    failed = 0
    
    for test_file in tests_to_run:
        test_path = test_dir / test_file
        if test_path.exists():
            if run_test(str(test_path)):
                passed += 1
            else:
                failed += 1
        else:
            print(f"⚠️  Test file not found: {test_file}")
            failed += 1
    
    print(f"\n{'='*60}")
    print(f"📊 Test Results Summary")
    print(f"{'='*60}")
    print(f"✅ Passed: {passed}")
    print(f"❌ Failed: {failed}")
    print(f"📈 Total: {passed + failed}")
    
    if failed == 0:
        print(f"🎉 All tests passed! 🎉")
    else:
        print(f"💔 {failed} test(s) failed")
        sys.exit(1)

if __name__ == "__main__":
    main()
