#!/usr/bin/env python3
"""
Test script to verify the performance tracker charts are working properly
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from components.performance_tracker import PerformanceTracker

def test_performance_tracker():
    """Test the performance tracker charts"""
    print("🧪 Testing Performance Tracker Charts...")
    
    # Initialize the performance tracker
    tracker = PerformanceTracker()
    
    # Test radar chart
    print("📊 Testing radar chart...")
    radar_fig = tracker.create_progress_radar()
    print(f"✅ Radar chart created: {type(radar_fig)}")
    
    # Test weekly progress chart
    print("📈 Testing weekly progress chart...")
    progress_fig = tracker.create_weekly_progress_chart()
    print(f"✅ Weekly progress chart created: {type(progress_fig)}")
    
    # Test study hours chart
    print("⏱️ Testing study hours chart...")
    hours_fig = tracker.create_study_hours_chart()
    print(f"✅ Study hours chart created: {type(hours_fig)}")
    
    print("🎉 All charts tested successfully!")
    return True

if __name__ == "__main__":
    try:
        test_performance_tracker()
        print("✅ All tests passed!")
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)
