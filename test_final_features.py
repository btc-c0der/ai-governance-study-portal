#!/usr/bin/env python3
"""
Final test to validate all implemented features:
1. Mark Complete button functionality
2. Progress tracking and chart updates
3. AI Study Topics tab content
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from components.auth_manager import AuthManager
from components.performance_tracker import PerformanceTracker
from components.curriculum import CurriculumManager
from components.database_manager import DatabaseManager
import app

def test_mark_complete_functionality():
    """Test the mark complete button and progress tracking"""
    print("Testing Mark Complete functionality...")
    
    # Initialize components
    auth_manager = AuthManager()
    performance_tracker = PerformanceTracker()
    curriculum_manager = CurriculumManager(performance_tracker=performance_tracker)
    
    # Test user creation and login
    test_user = "test_user_final"
    test_password = "test_password"
    
    # Clean up any existing test user
    try:
        auth_manager.delete_user(test_user)
    except:
        pass
    
    # Create test user
    success, _ = auth_manager.create_user(test_user, test_password)
    assert success, "Failed to create test user"
    
    # Login test user
    success, _ = auth_manager.authenticate_user(test_user, test_password)
    assert success, "Failed to login test user"
    
    # Get initial progress
    initial_progress = performance_tracker.get_user_progress(test_user)
    print(f"Initial progress: {initial_progress}")
    
    # Mark a topic complete
    topic_name = "AI Fundamentals"
    curriculum_manager.mark_topic_complete(test_user, topic_name)
    
    # Get updated progress
    updated_progress = performance_tracker.get_user_progress(test_user)
    print(f"Updated progress: {updated_progress}")
    
    # Verify topic was marked complete
    assert topic_name in updated_progress['completed_topics'], "Topic was not marked complete"
    
    # Test chart generation
    chart_html = performance_tracker.generate_progress_chart(test_user)
    assert chart_html and len(chart_html) > 100, "Chart generation failed"
    
    print("✓ Mark Complete functionality working correctly")
    
    # Cleanup
    auth_manager.delete_user(test_user)

def test_ai_study_topics_content():
    """Test the AI Study Topics tab content"""
    print("Testing AI Study Topics content...")
    
    # Test each topic content function
    topics = [
        ("AI Fundamentals", app.get_ai_fundamentals_content),
        ("AI Models", app.get_ai_models_content),
        ("Advanced AI", app.get_advanced_ai_content),
        ("AI Technologies", app.get_ai_technologies_content),
        ("Ethics & Governance", app.get_ethics_governance_content)
    ]
    
    for topic_name, content_func in topics:
        try:
            content = content_func()
            assert content and len(content) > 500, f"Content for {topic_name} is too short or empty"
            assert "##" in content, f"Content for {topic_name} lacks proper markdown formatting"
            print(f"✓ {topic_name} content validated")
        except Exception as e:
            print(f"✗ Error in {topic_name} content: {e}")
            raise

def test_database_integrity():
    """Test database integrity and operations"""
    print("Testing database integrity...")
    
    db_manager = DatabaseManager()
    
    # Test table existence
    tables = db_manager.get_table_names()
    required_tables = ['users', 'user_progress', 'quiz_scores', 'curriculum_notes']
    
    for table in required_tables:
        assert table in tables, f"Required table '{table}' not found"
    
    print("✓ Database integrity confirmed")

def main():
    """Run all tests"""
    print("Running final feature validation tests...")
    print("=" * 50)
    
    try:
        test_mark_complete_functionality()
        test_ai_study_topics_content()
        test_database_integrity()
        
        print("=" * 50)
        print("🎉 ALL TESTS PASSED! All implemented features are working correctly.")
        print("\nFeatures validated:")
        print("✓ Mark Complete button with progress tracking")
        print("✓ Learning progress charts with immediate updates")
        print("✓ AI Study Topics tab with comprehensive content")
        print("✓ Database integrity and user management")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
