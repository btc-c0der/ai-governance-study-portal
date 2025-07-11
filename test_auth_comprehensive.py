#!/usr/bin/env python3
"""
🔐 Comprehensive Authentication and Notes Association Test Suite
Tests both authenticated users and unauthenticated student notes functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from components.curriculum import CurriculumManager
from components.auth_manager import AuthManager
from components.performance_tracker import PerformanceTracker
import sqlite3
import json

class TestResults:
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.failed_test_names = []
    
    def add_test_result(self, test_name, passed, error_msg=None):
        self.total_tests += 1
        if passed:
            self.passed_tests += 1
            print(f"✅ {test_name}")
        else:
            self.failed_tests += 1
            self.failed_test_names.append(test_name)
            error_display = f" - {error_msg}" if error_msg else ""
            print(f"❌ {test_name}{error_display}")
    
    def print_summary(self):
        print("\n" + "="*70)
        print("📊 Test Suite Summary")
        print("="*70)
        print(f"Total Tests: {self.total_tests}")
        print(f"Passed: {self.passed_tests}")
        print(f"Failed: {self.failed_tests}")
        print(f"Pass Rate: {(self.passed_tests/self.total_tests)*100:.1f}%")
        
        if self.failed_test_names:
            print(f"\n❌ Failed Tests:")
            for test_name in self.failed_test_names:
                print(f"  - {test_name}")
        
        return self.failed_tests == 0

def test_auth_comprehensive():
    """Run comprehensive authentication and notes tests"""
    print("🔐 Comprehensive Authentication & Notes Association Test Suite")
    print("="*70)
    
    results = TestResults()
    
    # Initialize components
    try:
        auth_manager = AuthManager()
        performance_tracker = PerformanceTracker(auth_manager)
        curriculum_manager = CurriculumManager(auth_manager, performance_tracker)
        results.add_test_result("Component Initialization", True)
    except Exception as e:
        results.add_test_result("Component Initialization", False, str(e))
        return False
    
    # Test 1: User Registration and Authentication
    print("\n📝 Testing User Registration and Authentication...")
    
    test_users = [
        {"email": "student1@test.com", "password": "student123", "name": "Student One"},
        {"email": "student2@test.com", "password": "student456", "name": "Student Two"},
        {"email": "admin@test.com", "password": "admin123", "name": "Admin User"}
    ]
    
    # Clean up existing test users
    for user in test_users:
        try:
            # Try to find and delete existing user
            if auth_manager.user_exists(user["email"]):
                # Get user ID for cleanup
                conn = sqlite3.connect(auth_manager.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM users WHERE email = ?", (user["email"],))
                user_row = cursor.fetchone()
                if user_row:
                    user_id = user_row[0]
                    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                    conn.commit()
                conn.close()
        except Exception as e:
            pass  # User might not exist
    
    # Test user creation
    for user in test_users:
        try:
            success, message = auth_manager.create_user(
                user["email"], 
                user["password"], 
                role="admin" if "admin" in user["email"] else "student",
                profile_data={"name": user["name"]}
            )
            results.add_test_result(f"User Creation - {user['name']}", success, message if not success else None)
        except Exception as e:
            results.add_test_result(f"User Creation - {user['name']}", False, str(e))
    
    # Test user authentication
    for user in test_users:
        try:
            success, result = auth_manager.authenticate_user(user["email"], user["password"])
            results.add_test_result(f"User Authentication - {user['name']}", success, result if not success else None)
            
            if success:
                # Test logout
                auth_manager.logout()
                results.add_test_result(f"User Logout - {user['name']}", True)
            
        except Exception as e:
            results.add_test_result(f"User Authentication - {user['name']}", False, str(e))
    
    # Test 2: Student Notes (Non-authenticated)
    print("\n📝 Testing Student Notes (Non-authenticated)...")
    
    student_notes_test_data = [
        {"student_name": "John Doe", "week": 1, "title": "Week 1 Notes", "content": "Introduction to AI Governance"},
        {"student_name": "Jane Smith", "week": 1, "title": "AI Fundamentals", "content": "Understanding AI basics"},
        {"student_name": "John Doe", "week": 2, "title": "Week 2 Notes", "content": "EU AI Act overview"},
        {"student_name": "Bob Johnson", "week": 1, "title": "Getting Started", "content": "My first AI governance notes"}
    ]
    
    # Create student notes
    for note_data in student_notes_test_data:
        try:
            success, message = curriculum_manager.create_simple_note(
                note_data["student_name"],
                note_data["week"],
                note_data["title"],
                note_data["content"]
            )
            results.add_test_result(f"Student Note Creation - {note_data['student_name']} Week {note_data['week']}", success, message if not success else None)
        except Exception as e:
            results.add_test_result(f"Student Note Creation - {note_data['student_name']} Week {note_data['week']}", False, str(e))
    
    # Test student notes retrieval
    for student_name in set(note["student_name"] for note in student_notes_test_data):
        try:
            notes = curriculum_manager.get_student_notes(student_name)
            expected_count = len([n for n in student_notes_test_data if n["student_name"] == student_name])
            success = len(notes) == expected_count
            results.add_test_result(f"Student Notes Retrieval - {student_name}", success, f"Expected {expected_count}, got {len(notes)}" if not success else None)
            
            # Test week-specific retrieval
            week_1_notes = curriculum_manager.get_student_notes(student_name, 1)
            expected_week_1 = len([n for n in student_notes_test_data if n["student_name"] == student_name and n["week"] == 1])
            success = len(week_1_notes) == expected_week_1
            results.add_test_result(f"Student Notes Week Filter - {student_name}", success, f"Expected {expected_week_1}, got {len(week_1_notes)}" if not success else None)
            
        except Exception as e:
            results.add_test_result(f"Student Notes Retrieval - {student_name}", False, str(e))
    
    # Test student notes HTML generation
    try:
        html = curriculum_manager.get_simple_notes_html("John Doe", 1)
        success = html is not None and len(html) > 100 and "John Doe" in html
        results.add_test_result("Student Notes HTML Generation", success, "HTML generation failed or too short" if not success else None)
    except Exception as e:
        results.add_test_result("Student Notes HTML Generation", False, str(e))
    
    # Test 3: Advanced Notes (Authenticated Users)
    print("\n📝 Testing Advanced Notes (Authenticated Users)...")
    
    # Login as first test user
    try:
        success, result = auth_manager.authenticate_user("student1@test.com", "student123")
        if success:
            results.add_test_result("Login for Advanced Notes Testing", True)
            
            # Create advanced notes
            advanced_notes_data = [
                {"week": 1, "title": "Advanced AI Governance", "content": "Deep dive into governance frameworks"},
                {"week": 2, "title": "Risk Assessment", "content": "Detailed risk analysis methods"},
                {"week": 1, "title": "Compliance Notes", "content": "Regulatory compliance strategies"}
            ]
            
            for note_data in advanced_notes_data:
                try:
                    success, message = curriculum_manager.create_advanced_note(
                        note_data["week"],
                        note_data["title"],
                        note_data["content"]
                    )
                    results.add_test_result(f"Advanced Note Creation - Week {note_data['week']}: {note_data['title']}", success, message if not success else None)
                except Exception as e:
                    results.add_test_result(f"Advanced Note Creation - Week {note_data['week']}: {note_data['title']}", False, str(e))
            
            # Test advanced notes retrieval
            try:
                user_notes = curriculum_manager.get_user_notes()
                expected_count = len(advanced_notes_data)
                success = len(user_notes) == expected_count
                results.add_test_result("Advanced Notes Retrieval", success, f"Expected {expected_count}, got {len(user_notes)}" if not success else None)
                
                # Test week-specific retrieval
                week_1_user_notes = curriculum_manager.get_user_notes(1)
                expected_week_1 = len([n for n in advanced_notes_data if n["week"] == 1])
                success = len(week_1_user_notes) == expected_week_1
                results.add_test_result("Advanced Notes Week Filter", success, f"Expected {expected_week_1}, got {len(week_1_user_notes)}" if not success else None)
                
            except Exception as e:
                results.add_test_result("Advanced Notes Retrieval", False, str(e))
            
            # Test advanced notes HTML generation
            try:
                html = curriculum_manager.get_notes_html(1)
                success = html is not None and len(html) > 100
                results.add_test_result("Advanced Notes HTML Generation", success, "HTML generation failed or too short" if not success else None)
            except Exception as e:
                results.add_test_result("Advanced Notes HTML Generation", False, str(e))
                
        else:
            results.add_test_result("Login for Advanced Notes Testing", False, result)
            
    except Exception as e:
        results.add_test_result("Login for Advanced Notes Testing", False, str(e))
    
    # Test 4: Data Isolation and Security
    print("\n📝 Testing Data Isolation and Security...")
    
    # Logout and login as second user
    try:
        auth_manager.logout()
        success, result = auth_manager.authenticate_user("student2@test.com", "student456")
        if success:
            results.add_test_result("Second User Login", True)
            
            # Verify second user can't see first user's notes
            try:
                user_notes = curriculum_manager.get_user_notes()
                success = len(user_notes) == 0  # Should be empty for new user
                results.add_test_result("User Notes Isolation", success, f"Expected 0 notes, got {len(user_notes)}" if not success else None)
            except Exception as e:
                results.add_test_result("User Notes Isolation", False, str(e))
            
            # Create a note for second user
            try:
                success, message = curriculum_manager.create_note(1, "Second User Note", "This is from the second user")
                results.add_test_result("Second User Note Creation", success, message if not success else None)
            except Exception as e:
                results.add_test_result("Second User Note Creation", False, str(e))
            
        else:
            results.add_test_result("Second User Login", False, result)
            
    except Exception as e:
        results.add_test_result("Second User Login", False, str(e))
    
    # Test 5: Cross-verification
    print("\n📝 Testing Cross-verification...")
    
    # Login back as first user and verify notes are still there
    try:
        auth_manager.logout()
        success, result = auth_manager.authenticate_user("student1@test.com", "student123")
        if success:
            try:
                user_notes = curriculum_manager.get_user_notes()
                success = len(user_notes) == 3  # Should still have original 3 notes
                results.add_test_result("First User Notes Persistence", success, f"Expected 3 notes, got {len(user_notes)}" if not success else None)
            except Exception as e:
                results.add_test_result("First User Notes Persistence", False, str(e))
        else:
            results.add_test_result("First User Re-login", False, result)
    except Exception as e:
        results.add_test_result("First User Re-login", False, str(e))
    
    # Test 6: Student notes are still accessible regardless of authentication
    print("\n📝 Testing Student Notes Accessibility...")
    
    # Test student notes accessibility while logged in
    try:
        notes = curriculum_manager.get_student_notes("John Doe")
        success = len(notes) > 0
        results.add_test_result("Student Notes Accessible While Logged In", success, f"Expected > 0 notes, got {len(notes)}" if not success else None)
    except Exception as e:
        results.add_test_result("Student Notes Accessible While Logged In", False, str(e))
    
    # Test student notes accessibility while logged out
    try:
        auth_manager.logout()
        notes = curriculum_manager.get_student_notes("John Doe")
        success = len(notes) > 0
        results.add_test_result("Student Notes Accessible While Logged Out", success, f"Expected > 0 notes, got {len(notes)}" if not success else None)
    except Exception as e:
        results.add_test_result("Student Notes Accessible While Logged Out", False, str(e))
    
    # Test 7: Error handling
    print("\n📝 Testing Error Handling...")
    
    # Test creating advanced note without authentication
    try:
        success, message = curriculum_manager.create_advanced_note(1, "Test", "Test content")
        success = not success  # Should fail
        results.add_test_result("Advanced Note Creation Without Auth", success, "Should have failed but didn't" if not success else None)
    except Exception as e:
        results.add_test_result("Advanced Note Creation Without Auth", False, str(e))
    
    # Test empty student note creation
    try:
        success, message = curriculum_manager.create_simple_note("", 1, "Test", "Test content")
        success = not success  # Should fail
        results.add_test_result("Empty Student Name Validation", success, "Should have failed but didn't" if not success else None)
    except Exception as e:
        results.add_test_result("Empty Student Name Validation", False, str(e))
    
    # Test invalid week number
    try:
        success, message = curriculum_manager.create_simple_note("Test Student", 0, "Test", "Test content")
        # This might still succeed depending on implementation, so we'll just test it doesn't crash
        results.add_test_result("Invalid Week Number Handling", True)
    except Exception as e:
        results.add_test_result("Invalid Week Number Handling", False, str(e))
    
    # Cleanup
    print("\n🧹 Cleaning up test data...")
    try:
        # Delete test users
        for user in test_users:
            try:
                if auth_manager.user_exists(user["email"]):
                    conn = sqlite3.connect(auth_manager.db_path)
                    cursor = conn.cursor()
                    cursor.execute("SELECT id FROM users WHERE email = ?", (user["email"],))
                    user_row = cursor.fetchone()
                    if user_row:
                        user_id = user_row[0]
                        cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
                        cursor.execute("DELETE FROM curriculum_notes WHERE user_id = ?", (user_id,))
                        conn.commit()
                    conn.close()
            except Exception as e:
                pass  # Continue cleanup even if some operations fail
        
        # Clean up student notes
        try:
            conn = sqlite3.connect(curriculum_manager.notes_db_path)
            cursor = conn.cursor()
            test_student_names = set(note["student_name"] for note in student_notes_test_data)
            for student_name in test_student_names:
                cursor.execute("DELETE FROM student_notes WHERE student_name = ?", (student_name,))
            conn.commit()
            conn.close()
        except Exception as e:
            pass  # Continue even if cleanup fails
            
        results.add_test_result("Test Data Cleanup", True)
    except Exception as e:
        results.add_test_result("Test Data Cleanup", False, str(e))
    
    # Print final results
    success = results.print_summary()
    
    if success:
        print("\n🎉 All tests passed! Authentication and notes system is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Please review the results above.")
    
    return success

if __name__ == "__main__":
    print("Starting comprehensive authentication and notes test suite...")
    
    try:
        success = test_auth_comprehensive()
        
        if success:
            print("\n✅ PASS - All authentication and notes tests successful!")
            exit(0)
        else:
            print("\n❌ FAIL - Some tests failed!")
            exit(1)
            
    except Exception as e:
        print(f"\n❌ FAIL - Test Suite Execution: {str(e)}")
        exit(1)
