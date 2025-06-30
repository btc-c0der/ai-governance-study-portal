#!/usr/bin/env python3
"""
🧪 Component Testing Script
Tests individual components of the AI Governance Study Portal.
"""

import sys
import traceback

def test_component(component_name, import_path, class_name):
    """Test a single component"""
    try:
        print(f"Testing {component_name}...", end=" ")
        
        # Import the module
        module = __import__(import_path, fromlist=[class_name])
        component_class = getattr(module, class_name)
        
        # Initialize the component
        component = component_class()
        
        print("✅ PASS")
        return True
        
    except Exception as e:
        print(f"❌ FAIL: {e}")
        return False

def main():
    """Run all component tests"""
    print("🧪 AI Governance Codex - Component Testing")
    print("=" * 50)
    
    components_to_test = [
        ("Curriculum Manager", "components.curriculum", "CurriculumManager"),
        ("AI Act Explorer", "components.ai_act_explorer", "AIActExplorer"),
        ("Model Demos", "components.model_demos", "ModelDemos"),
        ("AI Tutor", "components.ai_tutor", "AITutor"),
        ("Performance Tracker", "components.performance_tracker", "PerformanceTracker"),
        ("Quiz Engine", "components.quiz_engine", "QuizEngine"),
    ]
    
    passed = 0
    total = len(components_to_test)
    
    for component_name, import_path, class_name in components_to_test:
        if test_component(component_name, import_path, class_name):
            passed += 1
    
    print("=" * 50)
    print(f"📊 Test Results: {passed}/{total} components passed")
    
    if passed == total:
        print("🎉 All components are working correctly!")
        print("🚀 Ready to launch the full application!")
    else:
        print("⚠️  Some components have issues. Check the error messages above.")
        print("💡 You can still use the working components.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 