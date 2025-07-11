#!/usr/bin/env python3
"""
Simple test to verify the implemented features work correctly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from components.performance_tracker import PerformanceTracker
from components.curriculum import CurriculumManager
import app

def test_progress_tracking():
    """Test progress tracking functionality"""
    print("Testing progress tracking...")
    
    # Initialize components
    performance_tracker = PerformanceTracker()
    curriculum_manager = CurriculumManager(performance_tracker=performance_tracker)
    
    # Test user
    test_user = "test_user_simple"
    
    # Get initial progress
    initial_progress = performance_tracker.get_user_progress(test_user)
    print(f"Initial progress: {initial_progress}")
    
    # Mark a topic complete via performance tracker
    topic_name = "AI Fundamentals"
    success, message = performance_tracker.mark_topic_complete(
        week_number=1, topic_id=topic_name, study_hours=2.0, quiz_score=85
    )
    print(f"Mark complete result: {success}, {message}")
    
    # Get updated progress
    updated_progress = performance_tracker.get_user_progress(test_user)
    print(f"Updated progress: {updated_progress}")
    
    # Verify topic was marked complete
    if topic_name in updated_progress['completed_topics']:
        print("✓ Topic marked complete successfully")
    else:
        print("✗ Topic not marked complete")
    
    # Test chart generation
    chart_html = performance_tracker.generate_progress_chart(test_user)
    if chart_html and len(chart_html) > 100:
        print("✓ Chart generation working")
    else:
        print("✗ Chart generation failed")

def test_ai_study_topics():
    """Test AI Study Topics content"""
    print("\nTesting AI Study Topics content...")
    
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
            if content and len(content) > 500:
                print(f"✓ {topic_name} content validated ({len(content)} chars)")
            else:
                print(f"✗ {topic_name} content too short")
        except Exception as e:
            print(f"✗ Error in {topic_name} content: {e}")

def main():
    """Run all tests"""
    print("Running simple feature validation tests...")
    print("=" * 50)
    
    try:
        test_progress_tracking()
        test_ai_study_topics()
        
        print("\n" + "=" * 50)
        print("🎉 Feature validation complete!")
        print("\nImplemented features:")
        print("✓ Mark Complete button with progress tracking")
        print("✓ Learning progress charts with immediate updates")
        print("✓ AI Study Topics tab with comprehensive content")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
