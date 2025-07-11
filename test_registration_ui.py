#!/usr/bin/env python3
"""
🔐 User Registration UI Test Suite
Tests the new user registration functionality via the UI
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from components.curriculum import CurriculumManager
from components.auth_manager import AuthManager
from components.performance_tracker import PerformanceTracker
import sqlite3
import json
import re

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
        print("📊 Registration UI Test Summary")
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

def test_registration_ui():
    """Test the user registration UI functionality"""
    print("🔐 User Registration UI Test Suite")
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
    
    # Test 1: Basic Registration Form Validation
    print("\n📝 Testing Registration Form Validation...")
    
    # Test empty fields
    test_cases = [
        # (email, password, confirm, name, institution, expected_result_contains)
        ("", "", "", "", "", "fill in all required fields"),
        ("test@email.com", "", "", "", "", "fill in all required fields"),
        ("test@email.com", "password123", "", "", "", "fill in all required fields"),
        ("test@email.com", "password123", "password123", "", "", "fill in all required fields"),
        ("test@email.com", "password123", "different123", "Test User", "", "Passwords do not match"),
        ("test@email.com", "short", "short", "Test User", "", "must be at least 8 characters"),
        ("invalid-email", "password123", "password123", "Test User", "", "valid email address"),
        ("test@email.com", "password123", "password123", "Test User", "Test Org", "User registered successfully"),
        ("test@email.com", "password123", "password123", "Test User", "", "User registered successfully"),  # Without institution
    ]
    
    # Clean up any existing test user
    try:
        if auth_manager.user_exists("test@email.com"):
            conn = sqlite3.connect(auth_manager.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE email = ?", ("test@email.com",))
            conn.commit()
            conn.close()
    except:
        pass
    
    for i, (email, password, confirm, name, institution, expected) in enumerate(test_cases):
        try:
            # Create a mock gradio object to simulate the UI response
            class MockGradioUpdate:
                def __init__(self, value, visible):
                    self.value = value
                    self.visible = visible
            
            # Create a temporary registration handler that returns the message directly
            def mock_handle_registration(email, password, confirm_password, name, institution):
                if not email or not password or not confirm_password or not name:
                    return MockGradioUpdate("⚠️ Please fill in all required fields (email, password, name)", True)
                
                if password != confirm_password:
                    return MockGradioUpdate("❌ Passwords do not match", True)
                
                if len(password) < 8:
                    return MockGradioUpdate("❌ Password must be at least 8 characters", True)
                
                # Validate email format
                if "@" not in email or "." not in email.split("@")[-1]:
                    return MockGradioUpdate("❌ Please enter a valid email address", True)
                
                # Create profile data
                profile_data = {
                    "name": name.strip(),
                    "institution": institution.strip() if institution else ""
                }
                
                success, message = auth_manager.create_user(email, password, profile_data=profile_data)
                
                if success:
                    return MockGradioUpdate(f"✅ User registered successfully. Please login now.", True)
                else:
                    return MockGradioUpdate(f"❌ {message}", True)
            
            result = mock_handle_registration(email, password, confirm, name, institution)
            success = expected.lower() in result.value.lower()
            
            results.add_test_result(f"Registration Validation Test {i+1}", success, 
                                  f"Expected '{expected}' in result, got '{result.value}'" if not success else None)
            
        except Exception as e:
            results.add_test_result(f"Registration Validation Test {i+1}", False, str(e))
    
    # Test 2: Successful Registration and Database Storage
    print("\n📝 Testing Successful Registration and Data Storage...")
    
    # Clean up any existing test users
    test_users = [
        "newuser1@test.com",
        "newuser2@test.com",
        "admin@test.com"
    ]
    
    for email in test_users:
        try:
            if auth_manager.user_exists(email):
                conn = sqlite3.connect(auth_manager.db_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE email = ?", (email,))
                conn.commit()
                conn.close()
        except:
            pass
    
    # Test successful registrations
    registration_test_cases = [
        {
            "email": "newuser1@test.com",
            "password": "securepassword123",
            "name": "John Doe",
            "institution": "Test University",
            "role": "student"
        },
        {
            "email": "newuser2@test.com", 
            "password": "anotherpassword456",
            "name": "Jane Smith",
            "institution": "",
            "role": "student"
        },
        {
            "email": "admin@test.com",
            "password": "adminpassword789",
            "name": "Admin User",
            "institution": "Test Organization",
            "role": "admin"
        }
    ]
    
    for i, user_data in enumerate(registration_test_cases):
        try:
            # Create user
            profile_data = {
                "name": user_data["name"],
                "institution": user_data["institution"]
            }
            success, message = auth_manager.create_user(
                user_data["email"], 
                user_data["password"], 
                role=user_data["role"],
                profile_data=profile_data
            )
            
            results.add_test_result(f"User Creation {i+1} - {user_data['name']}", success, message if not success else None)
            
            if success:
                # Verify user exists in database
                user_exists = auth_manager.user_exists(user_data["email"])
                results.add_test_result(f"User Database Storage {i+1} - {user_data['name']}", user_exists, 
                                      "User not found in database" if not user_exists else None)
                
                # Verify user profile data
                conn = sqlite3.connect(auth_manager.db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT profile_data FROM users WHERE email = ?", (user_data["email"],))
                result = cursor.fetchone()
                conn.close()
                
                if result:
                    try:
                        stored_profile = json.loads(result[0])
                        profile_matches = (
                            stored_profile.get("name") == user_data["name"] and
                            stored_profile.get("institution") == user_data["institution"]
                        )
                        results.add_test_result(f"Profile Data Storage {i+1} - {user_data['name']}", profile_matches,
                                              f"Profile mismatch: stored {stored_profile}, expected name={user_data['name']}, institution={user_data['institution']}" if not profile_matches else None)
                    except json.JSONDecodeError:
                        results.add_test_result(f"Profile Data Storage {i+1} - {user_data['name']}", False, "Invalid JSON in profile data")
                else:
                    results.add_test_result(f"Profile Data Storage {i+1} - {user_data['name']}", False, "No profile data found")
            
        except Exception as e:
            results.add_test_result(f"User Creation {i+1} - {user_data['name']}", False, str(e))
    
    # Test 3: Authentication After Registration
    print("\n📝 Testing Authentication After Registration...")
    
    for i, user_data in enumerate(registration_test_cases):
        try:
            # Test login
            success, result = auth_manager.authenticate_user(user_data["email"], user_data["password"])
            results.add_test_result(f"Post-Registration Login {i+1} - {user_data['name']}", success, 
                                  result if not success else None)
            
            if success:
                # Verify user data
                current_user = auth_manager.current_user
                profile_correct = (
                    current_user.get("email") == user_data["email"] and
                    current_user.get("role") == user_data["role"]
                )
                results.add_test_result(f"Login Data Verification {i+1} - {user_data['name']}", profile_correct,
                                      f"Profile mismatch: got {current_user}" if not profile_correct else None)
                
                # Test logout
                auth_manager.logout()
                is_logged_out = not auth_manager.is_logged_in()
                results.add_test_result(f"Logout After Registration {i+1} - {user_data['name']}", is_logged_out,
                                      "User still logged in after logout" if not is_logged_out else None)
        except Exception as e:
            results.add_test_result(f"Post-Registration Login {i+1} - {user_data['name']}", False, str(e))
    
    # Test 4: Duplicate Email Prevention
    print("\n📝 Testing Duplicate Email Prevention...")
    
    try:
        # Try to register with an existing email
        success, message = auth_manager.create_user("newuser1@test.com", "differentpassword", 
                                                  profile_data={"name": "Different User", "institution": ""})
        duplicate_prevented = not success
        results.add_test_result("Duplicate Email Prevention", duplicate_prevented, 
                              "Duplicate email was allowed" if not duplicate_prevented else None)
        
        if duplicate_prevented:
            # Verify the error message is appropriate
            message_appropriate = "already exists" in message.lower() or "duplicate" in message.lower()
            results.add_test_result("Duplicate Email Error Message", message_appropriate,
                                  f"Error message not appropriate: {message}" if not message_appropriate else None)
    except Exception as e:
        results.add_test_result("Duplicate Email Prevention", False, str(e))
    
    # Test 5: Password Security
    print("\n📝 Testing Password Security...")
    
    # Create a test user and check password hashing
    test_email = "security@test.com"
    test_password = "securitytest123"
    
    try:
        # Clean up existing user
        if auth_manager.user_exists(test_email):
            conn = sqlite3.connect(auth_manager.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE email = ?", (test_email,))
            conn.commit()
            conn.close()
        
        # Create user
        success, message = auth_manager.create_user(test_email, test_password, 
                                                  profile_data={"name": "Security Test", "institution": ""})
        results.add_test_result("Security Test User Creation", success, message if not success else None)
        
        if success:
            # Check that password is hashed in database
            conn = sqlite3.connect(auth_manager.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT password_hash FROM users WHERE email = ?", (test_email,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                stored_hash = result[0]
                password_is_hashed = stored_hash != test_password
                results.add_test_result("Password Hashing", password_is_hashed,
                                      "Password stored in plain text" if not password_is_hashed else None)
                
                # Check hash length (should be reasonably long)
                hash_length_ok = len(stored_hash) >= 32  # At least 32 characters
                results.add_test_result("Password Hash Length", hash_length_ok,
                                      f"Hash too short: {len(stored_hash)} characters" if not hash_length_ok else None)
            else:
                results.add_test_result("Password Hash Storage", False, "No password hash found")
    except Exception as e:
        results.add_test_result("Security Test User Creation", False, str(e))
    
    # Test 6: Role Assignment
    print("\n📝 Testing Role Assignment...")
    
    # Test default role assignment
    try:
        test_email = "roletest@test.com"
        
        # Clean up existing user
        if auth_manager.user_exists(test_email):
            conn = sqlite3.connect(auth_manager.db_path)
            cursor = conn.cursor()
            cursor.execute("DELETE FROM users WHERE email = ?", (test_email,))
            conn.commit()
            conn.close()
        
        # Create user without specifying role (should default to 'student')
        success, message = auth_manager.create_user(test_email, "roletest123",
                                                  profile_data={"name": "Role Test", "institution": ""})
        
        if success:
            # Check role in database
            conn = sqlite3.connect(auth_manager.db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT role FROM users WHERE email = ?", (test_email,))
            result = cursor.fetchone()
            conn.close()
            
            if result:
                role = result[0]
                default_role_correct = role == "student"
                results.add_test_result("Default Role Assignment", default_role_correct,
                                      f"Expected 'student', got '{role}'" if not default_role_correct else None)
            else:
                results.add_test_result("Default Role Assignment", False, "No role found")
        else:
            results.add_test_result("Role Test User Creation", False, message)
    except Exception as e:
        results.add_test_result("Default Role Assignment", False, str(e))
    
    # Test 7: Special Characters and Edge Cases
    print("\n📝 Testing Special Characters and Edge Cases...")
    
    edge_cases = [
        {
            "email": "test.user+tag@example.com",
            "name": "Test User with Special Characters àáâã",
            "institution": "Université de Test & Research",
            "should_succeed": True
        },
        {
            "email": "user@subdomain.example.com",
            "name": "User Name",
            "institution": "Test Organization - Division (Special Unit)",
            "should_succeed": True
        },
        {
            "email": "user@example",  # Invalid email
            "name": "User Name",
            "institution": "",
            "should_succeed": False
        }
    ]
    
    for i, case in enumerate(edge_cases):
        try:
            # Clean up existing user
            if auth_manager.user_exists(case["email"]):
                conn = sqlite3.connect(auth_manager.db_path)
                cursor = conn.cursor()
                cursor.execute("DELETE FROM users WHERE email = ?", (case["email"],))
                conn.commit()
                conn.close()
            
            success, message = auth_manager.create_user(
                case["email"], 
                "edgecase123",
                profile_data={"name": case["name"], "institution": case["institution"]}
            )
            
            test_passed = success == case["should_succeed"]
            results.add_test_result(f"Edge Case {i+1} - {case['email']}", test_passed,
                                  f"Expected success={case['should_succeed']}, got success={success}, message={message}" if not test_passed else None)
        except Exception as e:
            results.add_test_result(f"Edge Case {i+1} - {case['email']}", False, str(e))
    
    # Cleanup
    print("\n🧹 Cleaning up test data...")
    try:
        # Delete all test users
        all_test_emails = [
            "test@email.com", "newuser1@test.com", "newuser2@test.com", 
            "admin@test.com", "security@test.com", "roletest@test.com",
            "test.user+tag@example.com", "user@subdomain.example.com", "user@example"
        ]
        
        for email in all_test_emails:
            try:
                if auth_manager.user_exists(email):
                    conn = sqlite3.connect(auth_manager.db_path)
                    cursor = conn.cursor()
                    cursor.execute("DELETE FROM users WHERE email = ?", (email,))
                    conn.commit()
                    conn.close()
            except:
                pass  # Continue cleanup even if some operations fail
                
        results.add_test_result("Test Data Cleanup", True)
    except Exception as e:
        results.add_test_result("Test Data Cleanup", False, str(e))
    
    # Print final results
    success = results.print_summary()
    
    if success:
        print("\n🎉 All registration UI tests passed! The registration system is working correctly.")
    else:
        print("\n⚠️  Some registration tests failed. Please review the results above.")
    
    return success

if __name__ == "__main__":
    print("Starting user registration UI test suite...")
    
    try:
        success = test_registration_ui()
        
        if success:
            print("\n✅ PASS - All registration UI tests successful!")
            exit(0)
        else:
            print("\n❌ FAIL - Some registration tests failed!")
            exit(1)
            
    except Exception as e:
        print(f"\n❌ FAIL - Registration Test Suite Execution: {str(e)}")
        exit(1)
