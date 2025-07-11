#!/usr/bin/env python3
"""
Test script to verify the enhanced notes functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.curriculum import CurriculumManager
from components.auth_manager import AuthManager
from components.performance_tracker import PerformanceTracker

def test_notes_functionality():
    """Test the notes functionality"""
    print("🧪 Testing Enhanced Notes Functionality")
    print("=" * 50)
    
    # Initialize components
    auth_manager = AuthManager()
    performance_tracker = PerformanceTracker()
    curriculum_manager = CurriculumManager(performance_tracker=performance_tracker)
    
    # Test simple note creation
    print("1. Testing simple note creation...")
    success, message = curriculum_manager.create_simple_note(
        student_name="John Doe",
        week_number=1,
        title="Introduction to AI Governance",
        content="This week covers the basics of AI governance including regulatory frameworks and ethical considerations."
    )
    
    if success:
        print(f"✅ {message}")
    else:
        print(f"❌ {message}")
    
    # Test note retrieval
    print("\n2. Testing note retrieval...")
    notes = curriculum_manager.get_student_notes("John Doe", 1)
    if notes:
        print(f"✅ Retrieved {len(notes)} note(s) for John Doe, Week 1")
        for note in notes:
            print(f"   - {note['title']}")
    else:
        print("❌ No notes found")
    
    # Test HTML generation
    print("\n3. Testing HTML generation...")
    html = curriculum_manager.get_simple_notes_html("John Doe", 1)
    if html and len(html) > 100:
        print("✅ HTML generation working")
        print(f"   Generated {len(html)} characters of HTML")
    else:
        print("❌ HTML generation failed")
    
    # Test with different student
    print("\n4. Testing with different student...")
    success2, message2 = curriculum_manager.create_simple_note(
        student_name="Jane Smith",
        week_number=2,
        title="Risk Assessment Methods",
        content="Learning about different approaches to AI risk assessment."
    )
    
    if success2:
        print(f"✅ {message2}")
    else:
        print(f"❌ {message2}")
    
    # Test retrieval for all weeks
    print("\n5. Testing retrieval for all weeks...")
    all_notes = curriculum_manager.get_student_notes("John Doe")
    if all_notes:
        print(f"✅ Retrieved {len(all_notes)} total note(s) for John Doe")
    else:
        print("❌ No notes found for all weeks")
    
    print("\n" + "=" * 50)
    print("🎉 Notes functionality test complete!")

if __name__ == "__main__":
    test_notes_functionality()
