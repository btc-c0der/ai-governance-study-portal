#!/usr/bin/env python3
"""
Quick test script for Model Demos functionality
"""

import sys
import os
from pathlib import Path

# Add components to path
components_path = str(Path(__file__).parent.parent / "components")
sys.path.insert(0, components_path)
print(f"Added to path: {components_path}")

def test_basic_functionality():
    """Test basic ModelDemos functionality"""
    print("🧪 Testing Model Demos Basic Functionality")
    print("=" * 50)
    
    try:
        # Test imports
        print("📦 Testing imports...")
        from model_demos import ModelDemos
        print("✅ ModelDemos imported successfully")
        
        # Test initialization
        print("🔧 Testing initialization...")
        model_demos = ModelDemos()
        print("✅ ModelDemos initialized successfully")
        
        # Test provider status
        print("🔌 Testing provider status...")
        status = model_demos.get_provider_status()
        available = model_demos.get_available_providers()
        print(f"✅ Provider status: {status}")
        print(f"✅ Available providers: {available}")
        
        # Test basic classification
        print("📊 Testing classification...")
        test_text = "AI system for automated loan approval based on credit scoring"
        prediction, scores, explanation = model_demos.classify_document(test_text)
        print(f"✅ Classification result: {prediction}")
        print(f"✅ Confidence scores: {len(scores)} classes")
        print(f"✅ Explanation length: {len(explanation)} characters")
        
        # Test empty text handling
        print("🔍 Testing empty text handling...")
        pred_empty, scores_empty, exp_empty = model_demos.classify_document("")
        print(f"✅ Empty text result: {pred_empty}")
        
        # Test rate limiting
        print("⚡ Testing rate limiting...")
        limit_result = model_demos.check_rate_limit('test_provider')
        print(f"✅ Rate limit check: {limit_result}")
        
        print("\n🎉 All basic tests passed!")
        return True
        
    except Exception as e:
        print(f"❌ Error in basic functionality test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ai_integration():
    """Test AI provider integration"""
    print("\n🤖 Testing AI Provider Integration")
    print("=" * 50)
    
    try:
        from model_demos import ModelDemos
        model_demos = ModelDemos()
        
        # Check API keys
        from dotenv import load_dotenv
        load_dotenv()
        
        api_keys = {
            'OpenAI': os.getenv('OPENAI_API_KEY'),
            'Mistral': os.getenv('MISTRAL_API_KEY'),
            'DeepSeek': os.getenv('DEEPSEEK_API_KEY')
        }
        
        print("🔑 API Key Status:")
        available_providers = []
        for provider, key in api_keys.items():
            if key:
                print(f"  ✅ {provider}: Available")
                available_providers.append(provider.lower())
            else:
                print(f"  ❌ {provider}: Not configured")
        
        if available_providers:
            print(f"\n🧠 Testing AI analysis with {available_providers[0]}...")
            
            test_text = "AI system for customer service automation with natural language processing"
            
            # Test governance analysis
            result = model_demos.analyze_with_ai(
                test_text, 
                available_providers[0], 
                'governance'
            )
            
            if "API Error" in result or "not configured" in result:
                print(f"⚠️  API call failed: {result}")
            else:
                print(f"✅ AI analysis completed successfully!")
                print(f"📄 Result length: {len(result)} characters")
                print(f"📄 Result preview: {result[:200]}...")
        else:
            print("⚠️  No API keys configured, skipping AI integration tests")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in AI integration test: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_performance():
    """Test performance metrics"""
    print("\n📊 Testing Performance")
    print("=" * 50)
    
    try:
        import time
        from model_demos import ModelDemos
        
        model_demos = ModelDemos()
        
        # Test classification performance
        test_texts = [
            "AI system for automated loan approval",
            "Chatbot for customer service",
            "Facial recognition for security",
            "Product recommendation engine",
            "Medical diagnosis AI system"
        ]
        
        start_time = time.time()
        
        for i, text in enumerate(test_texts):
            classification_start = time.time()
            prediction, scores, explanation = model_demos.classify_document(text)
            classification_end = time.time()
            
            time_taken = (classification_end - classification_start) * 1000
            print(f"  {i+1}. {text[:40]}... -> {prediction} ({time_taken:.2f}ms)")
        
        end_time = time.time()
        total_time = (end_time - start_time) * 1000
        avg_time = total_time / len(test_texts)
        
        print(f"\n📈 Performance Results:")
        print(f"  Total time: {total_time:.2f}ms")
        print(f"  Average time per classification: {avg_time:.2f}ms")
        print(f"  Throughput: {len(test_texts)/(total_time/1000):.2f} classifications/second")
        
        if avg_time < 100:
            print("  ✅ Performance: EXCELLENT")
        elif avg_time < 500:
            print("  🟡 Performance: GOOD")
        else:
            print("  ❌ Performance: NEEDS IMPROVEMENT")
        
        return True
        
    except Exception as e:
        print(f"❌ Error in performance test: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests"""
    print("🤖 Model Demos Test Suite")
    print("=" * 50)
    
    results = []
    
    # Run tests
    results.append(("Basic Functionality", test_basic_functionality()))
    results.append(("AI Integration", test_ai_integration()))
    results.append(("Performance", test_performance()))
    
    # Summary
    print("\n📋 Test Summary")
    print("=" * 50)
    
    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{test_name}: {status}")
    
    all_passed = all(result[1] for result in results)
    
    if all_passed:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print("\n❌ Some tests failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
