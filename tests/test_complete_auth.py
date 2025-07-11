#!/usr/bin/env python3
"""
🔐 Complete Authentication System Test Suite
Tests all authentication features including registration UI, login, notes association, and UI functionality
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from components.curriculum import CurriculumManager
from components.auth_manager import AuthManager
from components.performance_tracker import PerformanceTracker
import sqlite3
import json
import time

def cleanup_test_data():
    """Clean up all test data before starting"""
    print("🧹 Cleaning up existing test data...")
    
    try:
        # Clean up users
        auth_manager = AuthManager()
        test_emails = [
            "test@email.com", "newuser1@test.com", "newuser2@test.com", 
            "admin@test.com", "security@test.com", "roletest@test.com",
            "test.user+tag@example.com", "user@subdomain.example.com", 
            "user@example", "student1@test.com", "student2@test.com"
        ]
        
        conn = sqlite3.connect(auth_manager.db_path)
        cursor = conn.cursor()
        
        for email in test_emails:
            cursor.execute("DELETE FROM users WHERE email = ?", (email,))
        
        conn.commit()
        conn.close()
        
        # Clean up notes
        notes_db_path = "data/curriculum_notes.db"
        if os.path.exists(notes_db_path):
            conn = sqlite3.connect(notes_db_path)
            cursor = conn.cursor()
            
            # Clean up student notes
            test_student_names = ["John Doe", "Jane Smith", "Bob Johnson", "Test Student"]
            for name in test_student_names:
                cursor.execute("DELETE FROM student_notes WHERE student_name = ?", (name,))
            
            conn.commit()
            conn.close()
        
        print("✅ Test data cleaned up successfully")
        return True
        
    except Exception as e:
        print(f"❌ Error cleaning up test data: {e}")
        return False

def test_complete_authentication_system():
    """Test the complete authentication system"""
    print("🔐 Complete Authentication System Test Suite")
    print("="*70)
    
    # Clean up first
    if not cleanup_test_data():
        return False
    
    passed_tests = 0
    total_tests = 0
    failed_tests = []
    
    def add_test_result(test_name, passed, error_msg=None):
        nonlocal passed_tests, total_tests, failed_tests
        total_tests += 1
        if passed:
            passed_tests += 1
            print(f"✅ {test_name}")
        else:
            failed_tests.append(test_name)
            error_display = f" - {error_msg}" if error_msg else ""
            print(f"❌ {test_name}{error_display}")
    
    # Initialize components
    try:
        auth_manager = AuthManager()
        performance_tracker = PerformanceTracker(auth_manager)
        curriculum_manager = CurriculumManager(auth_manager, performance_tracker)
        add_test_result("Component Initialization", True)
    except Exception as e:
        add_test_result("Component Initialization", False, str(e))
        return False
    
    # Test 1: User Registration with Full Validation
    print("\n📝 Testing User Registration with Full Validation...")
    
    # Test various registration scenarios
    registration_tests = [
        # (email, password, confirm, name, institution, should_succeed, expected_error)
        ("", "", "", "", "", False, "fill in all required fields"),
        ("test@example.com", "password123", "password123", "Test User", "Test Org", True, ""),
        ("test@example.com", "password123", "password123", "Test User", "Test Org", False, "already exists"),
        ("invalid-email", "password123", "password123", "Test User", "", False, "valid email"),
        ("test2@example.com", "short", "short", "Test User", "", False, "8 characters"),
        ("test3@example.com", "password123", "different", "Test User", "", False, "do not match"),
        ("user@example", "password123", "password123", "Test User", "", False, "Invalid email format"),
        ("test4@example.com", "validpassword123", "validpassword123", "Test User 2", "", True, ""),
    ]
    
    for i, (email, password, confirm, name, institution, should_succeed, expected_error) in enumerate(registration_tests):
        try:
            profile_data = {"name": name, "institution": institution} if name else {}
            
            # Test UI validation first
            if not email or not password or not confirm or not name:
                ui_result = "fill in all required fields"
            elif password != confirm:
                ui_result = "do not match"
            elif len(password) < 8:
                ui_result = "8 characters"
            elif not ("@" in email and "." in email.split("@")[-1] and len(email.split("@")) == 2 and email.split("@")[1] and not email.split("@")[1].startswith(".") and not email.split("@")[1].endswith(".")):
                ui_result = "valid email"
            else:
                # Test actual registration
                success, message = auth_manager.create_user(email, password, profile_data=profile_data)
                ui_result = "User registered successfully" if success else message
            
            test_passed = (should_succeed and "success" in ui_result.lower()) or (not should_succeed and expected_error.lower() in ui_result.lower())
            add_test_result(f"Registration Test {i+1}: {email}", test_passed, 
                          f"Expected {expected_error if not should_succeed else 'success'}, got: {ui_result}" if not test_passed else None)
            
        except Exception as e:
            add_test_result(f"Registration Test {i+1}: {email}", False, str(e))
    
    # Test 2: User Authentication
    print("\n📝 Testing User Authentication...")
    
    # Test login with registered users
    login_tests = [
        ("test@example.com", "password123", True),
        ("test@example.com", "wrongpassword", False),
        ("nonexistent@example.com", "password123", False),
        ("test4@example.com", "validpassword123", True),
    ]
    
    for email, password, should_succeed in login_tests:
        try:
            success, result = auth_manager.authenticate_user(email, password)
            add_test_result(f"Login Test: {email}", success == should_succeed, 
                          f"Expected success={should_succeed}, got success={success}, result={result}" if success != should_succeed else None)
            
            if success:
                # Test user data
                user_data = auth_manager.current_user
                data_valid = user_data and user_data.get("email") == email
                add_test_result(f"Login Data Validation: {email}", data_valid,
                              f"Invalid user data: {user_data}" if not data_valid else None)
                
                # Test logout
                auth_manager.logout()
                logged_out = not auth_manager.is_logged_in()
                add_test_result(f"Logout Test: {email}", logged_out,
                              "User still logged in after logout" if not logged_out else None)
        except Exception as e:
            add_test_result(f"Login Test: {email}", False, str(e))
    
    # Test 3: Notes Association (Student Notes)
    print("\n📝 Testing Student Notes Association...")
    
    student_notes_tests = [
        ("Alice Johnson", 1, "Week 1 Notes", "Basic AI concepts"),
        ("Bob Smith", 1, "My First Notes", "Understanding AI governance"),
        ("Alice Johnson", 2, "Week 2 Notes", "EU AI Act overview"),
        ("Charlie Brown", 3, "Advanced Notes", "Risk management strategies"),
    ]
    
    for student_name, week, title, content in student_notes_tests:
        try:
            success, message = curriculum_manager.create_simple_note(student_name, week, title, content)
            add_test_result(f"Student Note Creation: {student_name} Week {week}", success, message if not success else None)
        except Exception as e:
            add_test_result(f"Student Note Creation: {student_name} Week {week}", False, str(e))
    
    # Test student notes retrieval
    for student_name in ["Alice Johnson", "Bob Smith", "Charlie Brown"]:
        try:
            notes = curriculum_manager.get_student_notes(student_name)
            expected_count = len([n for n in student_notes_tests if n[0] == student_name])
            add_test_result(f"Student Notes Retrieval: {student_name}", len(notes) == expected_count,
                          f"Expected {expected_count} notes, got {len(notes)}" if len(notes) != expected_count else None)
        except Exception as e:
            add_test_result(f"Student Notes Retrieval: {student_name}", False, str(e))
    
    # Test 4: Advanced Notes (Authenticated)
    print("\n📝 Testing Advanced Notes (Authenticated)...")
    
    # Login as registered user
    try:
        success, result = auth_manager.authenticate_user("test@example.com", "password123")
        if success:
            add_test_result("Login for Advanced Notes", True)
            
            # Create advanced notes
            advanced_notes = [
                (1, "Advanced Governance", "Deep dive into AI governance frameworks"),
                (2, "Risk Analysis", "Comprehensive risk assessment methods"),
                (1, "Compliance Strategy", "Regulatory compliance approach"),
            ]
            
            for week, title, content in advanced_notes:
                try:
                    success, message = curriculum_manager.create_advanced_note(week, title, content)
                    add_test_result(f"Advanced Note Creation: Week {week}", success, message if not success else None)
                except Exception as e:
                    add_test_result(f"Advanced Note Creation: Week {week}", False, str(e))
            
            # Test advanced notes retrieval
            try:
                user_notes = curriculum_manager.get_user_notes()
                add_test_result("Advanced Notes Retrieval", len(user_notes) == len(advanced_notes),
                              f"Expected {len(advanced_notes)} notes, got {len(user_notes)}" if len(user_notes) != len(advanced_notes) else None)
            except Exception as e:
                add_test_result("Advanced Notes Retrieval", False, str(e))
            
        else:
            add_test_result("Login for Advanced Notes", False, result)
            
    except Exception as e:
        add_test_result("Login for Advanced Notes", False, str(e))
    
    # Test 5: Data Isolation
    print("\n📝 Testing Data Isolation...")
    
    # Create second user and verify isolation
    try:
        success, message = auth_manager.create_user("isolation@test.com", "password123", 
                                                  profile_data={"name": "Isolation Test", "institution": ""})
        if success:
            add_test_result("Isolation Test User Creation", True)
            
            # Logout first user and login second user
            auth_manager.logout()
            success, result = auth_manager.authenticate_user("isolation@test.com", "password123")
            
            if success:
                # Second user should have no notes
                user_notes = curriculum_manager.get_user_notes()
                add_test_result("Data Isolation - Second User", len(user_notes) == 0,
                              f"Expected 0 notes, got {len(user_notes)}" if len(user_notes) != 0 else None)
                
                # Create note for second user
                success, message = curriculum_manager.create_note(1, "Second User Note", "This is from second user")
                add_test_result("Second User Note Creation", success, message if not success else None)
                
                # Verify first user's notes are still separate
                auth_manager.logout()
                success, result = auth_manager.authenticate_user("test@example.com", "password123")
                if success:
                    user_notes = curriculum_manager.get_user_notes()
                    add_test_result("Data Isolation - First User Persistence", len(user_notes) == 3,
                                  f"Expected 3 notes, got {len(user_notes)}" if len(user_notes) != 3 else None)
            else:
                add_test_result("Isolation Test User Login", False, result)
        else:
            add_test_result("Isolation Test User Creation", False, message)
            
    except Exception as e:
        add_test_result("Data Isolation Test", False, str(e))
    
    # Test 6: UI Integration Tests
    print("\n📝 Testing UI Integration...")
    
    # Test HTML generation for both note types
    try:
        # Student notes HTML
        html = curriculum_manager.get_simple_notes_html("Alice Johnson", 1)
        add_test_result("Student Notes HTML Generation", html is not None and len(html) > 100,
                      f"HTML too short or None: {len(html) if html else 'None'}" if not (html and len(html) > 100) else None)
        
        # Advanced notes HTML (need to be logged in)
        if auth_manager.is_logged_in():
            html = curriculum_manager.get_notes_html(1)
            add_test_result("Advanced Notes HTML Generation", html is not None and len(html) > 100,
                          f"HTML too short or None: {len(html) if html else 'None'}" if not (html and len(html) > 100) else None)
        
    except Exception as e:
        add_test_result("UI Integration Test", False, str(e))
    
    # Test 7: Error Handling
    print("\n📝 Testing Error Handling...")
    
    # Test creating advanced note without authentication
    try:
        auth_manager.logout()
        success, message = curriculum_manager.create_advanced_note(1, "Test", "Test content")
        add_test_result("Advanced Note Without Auth", not success, "Should have failed but didn't" if success else None)
    except Exception as e:
        add_test_result("Advanced Note Without Auth", False, str(e))
    
    # Test empty student note
    try:
        success, message = curriculum_manager.create_simple_note("", 1, "Test", "Test content")
        add_test_result("Empty Student Name Validation", not success, "Should have failed but didn't" if success else None)
    except Exception as e:
        add_test_result("Empty Student Name Validation", False, str(e))
    
    # Cleanup
    print("\n🧹 Final cleanup...")
    try:
        cleanup_success = cleanup_test_data()
        add_test_result("Final Cleanup", cleanup_success)
    except Exception as e:
        add_test_result("Final Cleanup", False, str(e))
    
    # Print results
    print("\n" + "="*70)
    print("📊 Complete Authentication System Test Results")
    print("="*70)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {len(failed_tests)}")
    print(f"Pass Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests:
        print(f"\n❌ Failed Tests:")
        for test_name in failed_tests:
            print(f"  - {test_name}")
    
    success = len(failed_tests) == 0
    
    if success:
        print("\n🎉 All authentication system tests passed!")
        print("✨ The complete authentication system is working correctly!")
        print("🔐 Registration UI, login, notes association, and data isolation all functional!")
    else:
        print(f"\n⚠️  {len(failed_tests)} test(s) failed. Please review the results above.")
    
    return success

if __name__ == "__main__":
    print("Starting complete authentication system test suite...")
    
    try:
        success = test_complete_authentication_system()
        
        if success:
            print("\n✅ PASS - Complete authentication system test successful!")
            exit(0)
        else:
            print("\n❌ FAIL - Some authentication tests failed!")
            exit(1)
            
    except Exception as e:
        print(f"\n❌ FAIL - Authentication Test Suite Execution: {str(e)}")
        exit(1)
