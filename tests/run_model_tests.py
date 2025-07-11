#!/usr/bin/env python3
"""
Test runner for Model Demos with comprehensive coverage.
Includes unit tests, integration tests, and performance benchmarks.
"""

import os
import sys
import subprocess
import time
from pathlib import Path
from dotenv import load_dotenv
import argparse

# Load environment variables
load_dotenv()

def check_api_keys():
    """Check which API keys are available"""
    keys = {
        'OpenAI': os.getenv('OPENAI_API_KEY'),
        'Mistral': os.getenv('MISTRAL_API_KEY'),
        'DeepSeek': os.getenv('DEEPSEEK_API_KEY')
    }
    
    print("🔑 API Key Status:")
    available = []
    for provider, key in keys.items():
        if key:
            print(f"  ✅ {provider}: Available")
            available.append(provider.lower())
        else:
            print(f"  ❌ {provider}: Not configured")
    
    return available

def run_unit_tests():
    """Run unit tests for Model Demos"""
    print("\n🧪 Running Unit Tests...")
    
    cmd = [
        sys.executable, "-m", "pytest", 
        "tests/test_model_demos.py::TestModelDemos",
        "-v", "--tb=short"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Unit tests passed!")
    else:
        print("❌ Unit tests failed!")
        print(result.stdout)
        print(result.stderr)
    
    return result.returncode == 0

def run_integration_tests(available_providers):
    """Run integration tests with real API calls"""
    print("\n🌐 Running Integration Tests...")
    
    if not available_providers:
        print("⚠️  No API keys available, skipping integration tests")
        return True
    
    cmd = [
        sys.executable, "-m", "pytest", 
        "tests/test_model_demos.py::TestModelDemosIntegration",
        "-v", "--tb=short", "-m", "integration"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Integration tests passed!")
    else:
        print("❌ Integration tests failed!")
        print(result.stdout)
        print(result.stderr)
    
    return result.returncode == 0

def run_stress_tests():
    """Run stress tests for Model Demos"""
    print("\n💪 Running Stress Tests...")
    
    cmd = [
        sys.executable, "-m", "pytest", 
        "tests/test_model_demos.py::TestModelDemosStress",
        "-v", "--tb=short"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Stress tests passed!")
    else:
        print("❌ Stress tests failed!")
        print(result.stdout)
        print(result.stderr)
    
    return result.returncode == 0

def run_performance_benchmark():
    """Run performance benchmarks"""
    print("\n📊 Running Performance Benchmarks...")
    
    try:
        # Import here to avoid issues if model_demos isn't available
        sys.path.insert(0, str(Path(__file__).parent / "components"))
        from model_demos import ModelDemos
        
        model_demos = ModelDemos()
        
        # Test classification performance
        test_text = "AI system for automated loan approval based on credit scoring"
        
        start_time = time.time()
        prediction, scores, explanation = model_demos.classify_document(test_text)
        end_time = time.time()
        
        classification_time = (end_time - start_time) * 1000  # Convert to milliseconds
        
        print(f"  📈 Classification Time: {classification_time:.2f}ms")
        print(f"  🎯 Classification Result: {prediction}")
        print(f"  📊 Confidence Scores: {len(scores)} classes")
        
        # Test multiple classifications
        test_texts = [
            "Chatbot for customer service",
            "Facial recognition for security",
            "Product recommendation engine",
            "Medical diagnosis AI system",
            "Automated resume screening"
        ]
        
        start_time = time.time()
        for text in test_texts:
            model_demos.classify_document(text)
        end_time = time.time()
        
        batch_time = (end_time - start_time) * 1000
        avg_time = batch_time / len(test_texts)
        
        print(f"  🔄 Batch Processing ({len(test_texts)} docs): {batch_time:.2f}ms")
        print(f"  ⚡ Average Time per Document: {avg_time:.2f}ms")
        
        # Performance thresholds
        if classification_time < 1000:  # Less than 1 second
            print("  ✅ Classification performance: EXCELLENT")
        elif classification_time < 3000:  # Less than 3 seconds
            print("  🟡 Classification performance: GOOD")
        else:
            print("  ❌ Classification performance: NEEDS IMPROVEMENT")
        
        return True
        
    except Exception as e:
        print(f"  ❌ Performance benchmark failed: {e}")
        return False

def run_api_connectivity_test(available_providers):
    """Test API connectivity for available providers"""
    print("\n🔗 Testing API Connectivity...")
    
    if not available_providers:
        print("⚠️  No API keys available, skipping connectivity tests")
        return True
    
    try:
        sys.path.insert(0, str(Path(__file__).parent / "components"))
        from model_demos import ModelDemos
        
        model_demos = ModelDemos()
        
        for provider in available_providers:
            try:
                print(f"  📡 Testing {provider.title()} API...")
                
                # Simple test prompt
                result = model_demos.analyze_with_ai(
                    "Test AI system for basic functionality check",
                    provider,
                    "governance"
                )
                
                if "API Error" in result or "not configured" in result:
                    print(f"    ❌ {provider.title()}: Connection failed")
                else:
                    print(f"    ✅ {provider.title()}: Connected successfully")
                
            except Exception as e:
                print(f"    ❌ {provider.title()}: Error - {e}")
        
        return True
        
    except Exception as e:
        print(f"  ❌ API connectivity test failed: {e}")
        return False

def generate_test_report():
    """Generate a comprehensive test report"""
    print("\n📋 Generating Test Report...")
    
    cmd = [
        sys.executable, "-m", "pytest", 
        "tests/test_model_demos.py",
        "--tb=short",
        "--cov=components.model_demos",
        "--cov-report=html",
        "--cov-report=term-missing"
    ]
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode == 0:
            print("✅ Test report generated successfully!")
            print("📄 HTML report available at: htmlcov/index.html")
        else:
            print("⚠️  Test report generation completed with warnings")
        
        print(result.stdout)
        
    except Exception as e:
        print(f"❌ Test report generation failed: {e}")

def main():
    """Main test runner function"""
    parser = argparse.ArgumentParser(description="Model Demos Test Runner")
    parser.add_argument("--unit", action="store_true", help="Run unit tests only")
    parser.add_argument("--integration", action="store_true", help="Run integration tests only")
    parser.add_argument("--stress", action="store_true", help="Run stress tests only")
    parser.add_argument("--performance", action="store_true", help="Run performance benchmarks only")
    parser.add_argument("--connectivity", action="store_true", help="Test API connectivity only")
    parser.add_argument("--report", action="store_true", help="Generate test report")
    parser.add_argument("--all", action="store_true", help="Run all tests")
    
    args = parser.parse_args()
    
    print("🤖 Model Demos Test Suite")
    print("=" * 50)
    
    # Check API keys
    available_providers = check_api_keys()
    
    results = []
    
    # Run selected tests
    if args.unit or args.all:
        results.append(("Unit Tests", run_unit_tests()))
    
    if args.integration or args.all:
        results.append(("Integration Tests", run_integration_tests(available_providers)))
    
    if args.stress or args.all:
        results.append(("Stress Tests", run_stress_tests()))
    
    if args.performance or args.all:
        results.append(("Performance Benchmarks", run_performance_benchmark()))
    
    if args.connectivity or args.all:
        results.append(("API Connectivity", run_api_connectivity_test(available_providers)))
    
    if args.report or args.all:
        generate_test_report()
    
    # If no specific tests requested, run all
    if not any([args.unit, args.integration, args.stress, args.performance, args.connectivity, args.report]):
        results.append(("Unit Tests", run_unit_tests()))
        results.append(("Integration Tests", run_integration_tests(available_providers)))
        results.append(("Stress Tests", run_stress_tests()))
        results.append(("Performance Benchmarks", run_performance_benchmark()))
        results.append(("API Connectivity", run_api_connectivity_test(available_providers)))
        generate_test_report()
    
    # Print summary
    print("\n📊 Test Summary")
    print("=" * 50)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    # Overall result
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
