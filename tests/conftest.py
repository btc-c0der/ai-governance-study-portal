"""
Test configuration for Model Demos with API key management.
"""

import pytest
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables for testing
load_dotenv()

def pytest_configure(config):
    """Configure pytest for model demos testing"""
    # Add custom markers
    config.addinivalue_line(
        "markers", 
        "integration: marks tests as integration tests requiring API keys"
    )
    config.addinivalue_line(
        "markers",
        "slow: marks tests as slow running"
    )
    config.addinivalue_line(
        "markers",
        "real_api: marks tests that make real API calls"
    )

@pytest.fixture(scope="session")
def api_keys():
    """Fixture to provide API keys for testing"""
    return {
        'openai': os.getenv('OPENAI_API_KEY'),
        'mistral': os.getenv('MISTRAL_API_KEY'),
        'deepseek': os.getenv('DEEPSEEK_API_KEY')
    }

@pytest.fixture(scope="session")
def available_providers(api_keys):
    """Fixture to provide list of available providers"""
    return [provider for provider, key in api_keys.items() if key]

@pytest.fixture
def mock_api_responses():
    """Fixture providing mock API responses for testing"""
    return {
        'openai': {
            'governance': """
            ## EU AI Act Risk Assessment
            
            **Classification:** High Risk
            **Confidence:** 85%
            
            This AI system falls under the High Risk category according to Article 6 of the EU AI Act.
            
            ### Key Requirements:
            - Conformity assessment (Article 43)
            - Technical documentation (Annex IV)
            - Risk management system (Article 9)
            - Data governance (Article 10)
            - Transparency obligations (Article 13)
            """,
            'bias': """
            ## Bias Analysis Report
            
            **Bias Level:** Moderate
            **Affected Groups:** Gender, Age
            
            ### Identified Issues:
            1. Gender disparity in approval rates (15% difference)
            2. Age-based discrimination against younger applicants
            
            ### Mitigation Strategies:
            - Implement fairness constraints
            - Audit training data for representation
            - Monitor outcomes across demographics
            """,
            'explainability': """
            ## Explainability Requirements
            
            **Complexity Level:** High
            **Stakeholders:** End users, regulators, auditors
            
            ### Recommended Techniques:
            - LIME for local explanations
            - SHAP for feature importance
            - Counterfactual explanations
            - Natural language summaries
            """
        },
        'mistral': {
            'governance': """
            # Analyse de Gouvernance IA
            
            **Niveau de Risque:** Élevé
            **Conformité EU AI Act:** Requise
            
            Ce système nécessite une évaluation de conformité complète.
            """,
            'bias': """
            # Détection de Biais
            
            **Biais Identifié:** Oui
            **Gravité:** Modérée
            
            Des disparités ont été détectées dans les résultats.
            """,
            'explainability': """
            # Exigences d'Explicabilité
            
            **Niveau:** Avancé
            **Techniques:** SHAP, LIME recommandées
            """
        },
        'deepseek': {
            'governance': """
            # AI Governance Analysis
            
            ## Risk Classification
            Based on the system description, this falls under **High Risk** category.
            
            ## Compliance Requirements
            - Technical documentation required
            - Risk management system implementation
            - Post-market monitoring
            """,
            'bias': """
            # Bias Assessment
            
            ## Findings
            Potential bias detected in decision patterns.
            
            ## Recommendations
            - Implement fairness metrics
            - Regular bias audits
            - Diverse training data
            """,
            'explainability': """
            # Explainability Analysis
            
            ## Requirements
            High explainability needs for this use case.
            
            ## Implementation
            - Model-agnostic explanations
            - User-friendly interfaces
            - Regulatory compliance
            """
        }
    }

@pytest.fixture
def test_scenarios():
    """Fixture providing test scenarios for different AI systems"""
    return {
        'high_risk': [
            "AI system for automated loan approval using credit scoring and personal data",
            "Facial recognition system for law enforcement identification",
            "AI-powered medical diagnosis system for cancer detection",
            "Automated hiring system that screens resumes and ranks candidates"
        ],
        'limited_risk': [
            "Chatbot that assists customers with product information",
            "Content moderation system for social media platforms",
            "AI voice assistant for smart home control",
            "Automated email spam detection system"
        ],
        'minimal_risk': [
            "Product recommendation engine for e-commerce",
            "Predictive maintenance system for industrial equipment",
            "AI-powered search engine optimization",
            "Automated image tagging for photo organization"
        ],
        'biased_systems': [
            "Resume screening system showing gender disparities in tech roles",
            "Facial recognition with lower accuracy for certain ethnic groups",
            "Credit scoring algorithm with age-based discrimination",
            "Healthcare AI with geographic bias in treatment recommendations"
        ]
    }

@pytest.fixture
def performance_benchmarks():
    """Fixture providing performance benchmarks for testing"""
    return {
        'classification_accuracy': 0.85,
        'response_time_ms': 1000,
        'api_timeout_seconds': 30,
        'rate_limit_per_minute': 10,
        'memory_usage_mb': 100
    }

def skip_if_no_api_key(provider):
    """Skip test if API key is not available"""
    api_key = os.getenv(f'{provider.upper()}_API_KEY')
    return pytest.mark.skipif(
        not api_key, 
        reason=f"{provider} API key not available"
    )

def skip_if_no_internet():
    """Skip test if internet connection is not available"""
    import socket
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return pytest.mark.skipif(False, reason="")
    except OSError:
        return pytest.mark.skipif(True, reason="No internet connection")
