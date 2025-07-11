#!/usr/bin/env python3
"""
Comprehensive API integration test for all providers
"""

import sys
import os
from pathlib import Path
import asyncio

# Add components to path
components_path = str(Path(__file__).parent.parent / "components")
sys.path.insert(0, components_path)

from model_demos import ModelDemos
from dotenv import load_dotenv

load_dotenv()

async def test_all_providers():
    """Test all available API providers"""
    print("🔥 Comprehensive API Provider Test")
    print("=" * 50)
    
    model_demos = ModelDemos()
    available_providers = model_demos.get_available_providers()
    
    test_scenarios = [
        {
            'text': 'AI system for automated hiring decisions and resume screening',
            'analysis_type': 'governance',
            'expected_keywords': ['High Risk', 'EU AI Act', 'compliance', 'hiring']
        },
        {
            'text': 'Facial recognition system with different accuracy rates for different ethnic groups',
            'analysis_type': 'bias',
            'expected_keywords': ['bias', 'fairness', 'ethnic', 'discrimination']
        },
        {
            'text': 'Medical diagnosis AI system that doctors use to identify cancer',
            'analysis_type': 'explainability',
            'expected_keywords': ['explainability', 'medical', 'LIME', 'SHAP']
        }
    ]
    
    results = {}
    
    for provider in available_providers:
        print(f"\n🤖 Testing {provider.upper()} API")
        print("-" * 30)
        
        provider_results = []
        
        for i, scenario in enumerate(test_scenarios):
            print(f"  📋 Test {i+1}: {scenario['analysis_type'].title()} Analysis")
            
            try:
                result = await model_demos.call_ai_model(
                    provider,
                    f"Analyze this AI system for {scenario['analysis_type']}: {scenario['text']}",
                    f"You are an AI {scenario['analysis_type']} expert. Provide detailed analysis."
                )
                
                if any(error in result for error in ['API Error', 'timeout', 'not configured']):
                    print(f"    ❌ Failed: {result}")
                    provider_results.append(False)
                else:
                    print(f"    ✅ Success: {len(result)} characters")
                    
                    # Check for expected keywords
                    keywords_found = sum(1 for keyword in scenario['expected_keywords'] 
                                       if keyword.lower() in result.lower())
                    print(f"    🎯 Keywords found: {keywords_found}/{len(scenario['expected_keywords'])}")
                    
                    provider_results.append(True)
                    
            except Exception as e:
                print(f"    ❌ Error: {e}")
                provider_results.append(False)
        
        results[provider] = provider_results
        
        # Summary for this provider
        success_rate = sum(provider_results) / len(provider_results) * 100
        print(f"  📊 {provider.upper()} Success Rate: {success_rate:.1f}%")
    
    # Overall summary
    print(f"\n📈 Overall Results")
    print("=" * 50)
    
    for provider, provider_results in results.items():
        success_rate = sum(provider_results) / len(provider_results) * 100
        status = "✅" if success_rate >= 80 else "⚠️" if success_rate >= 50 else "❌"
        print(f"{status} {provider.upper()}: {success_rate:.1f}% ({sum(provider_results)}/{len(provider_results)} tests passed)")
    
    # Test provider switching
    print(f"\n🔄 Testing Provider Switching")
    print("-" * 30)
    
    test_text = "AI system for automated content moderation"
    
    for provider in available_providers:
        try:
            result = model_demos.analyze_with_ai(test_text, provider, 'governance')
            if any(error in result for error in ['API Error', 'timeout', 'not configured']):
                print(f"  ❌ {provider.upper()}: {result}")
            else:
                print(f"  ✅ {provider.upper()}: Analysis completed ({len(result)} chars)")
        except Exception as e:
            print(f"  ❌ {provider.upper()}: Error - {e}")
    
    print(f"\n🎉 Test completed!")

if __name__ == "__main__":
    asyncio.run(test_all_providers())
