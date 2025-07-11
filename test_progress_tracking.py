#!/usr/bin/env python3
"""
Test script to verify the progress tracking functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from components.performance_tracker import PerformanceTracker
from components.auth_manager import AuthManager

def test_progress_tracking():
    """Test the progress tracking functionality"""
    print("🧪 Testing Progress Tracking Functionality...")
    
    # Initialize components
    auth_manager = AuthManager()
    tracker = PerformanceTracker(auth_manager)
    
    # Test without authentication
    print("📊 Testing without authentication...")
    success, message = tracker.mark_topic_complete(1, "Test Topic", 2.0, 85.0)
    print(f"Result: {success}, Message: {message}")
    
    # Test get progress data
    print("📈 Testing progress data retrieval...")
    progress_data = tracker.get_user_progress()
    print(f"Progress data keys: {list(progress_data.keys())}")
    print(f"Weekly progress sample: {progress_data['weekly_progress'][:3]}...")
    
    # Test chart creation
    print("📊 Testing chart creation...")
    radar_fig = tracker.create_progress_radar()
    print(f"✅ Radar chart created: {type(radar_fig)}")
    
    progress_fig = tracker.create_weekly_progress_chart()
    print(f"✅ Progress chart created: {type(progress_fig)}")
    
    # Test refresh functionality
    print("🔄 Testing refresh functionality...")
    refreshed_data = tracker.refresh_progress_data()
    print(f"✅ Refresh completed: {type(refreshed_data)}")
    
    print("🎉 All progress tracking tests completed!")
    return True

if __name__ == "__main__":
    try:
        test_progress_tracking()
        print("✅ All tests passed!")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
