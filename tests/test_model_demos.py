"""
Test cases for Model Demos component with multi-provider support.
Tests OpenAI, Mistral, and DeepSeek API integrations.
"""

import pytest
import asyncio
import os
from unittest.mock import Mock, patch, AsyncMock
import sys
import json
from pathlib import Path

# Add the components directory to the path
sys.path.insert(0, str(Path(__file__).parent.parent / "components"))

from model_demos import ModelDemos

class TestModelDemos:
    """Test suite for Model Demos component"""
    
    @pytest.fixture
    def model_demos(self):
        """Create ModelDemos instance for testing"""
        return ModelDemos()
    
    @pytest.fixture
    def mock_env_vars(self):
        """Mock environment variables for testing"""
        return {
            'OPENAI_API_KEY': 'test_openai_key',
            'OPENAI_MODEL': 'gpt-4o-mini',
            'MISTRAL_API_KEY': 'test_mistral_key',
            'MISTRAL_MODEL': 'mistral-large-latest',
            'DEEPSEEK_API_KEY': 'test_deepseek_key',
            'DEEPSEEK_MODEL': 'deepseek-chat',
            'DEFAULT_MODEL_PROVIDER': 'openai',
            'API_TIMEOUT': '30',
            'MAX_TOKENS': '2000',
            'TEMPERATURE': '0.7',
            'ENABLE_AI_DEMOS': 'true',
            'DEMO_RATE_LIMIT': '10'
        }
    
    def test_initialization(self, model_demos):
        """Test ModelDemos initialization"""
        assert model_demos.legal_classifier is not None
        assert model_demos.sample_documents is not None
        assert model_demos.api_clients is not None
        assert model_demos.rate_limiter is not None
    
    def test_api_clients_setup(self, model_demos):
        """Test API clients setup"""
        clients = model_demos.api_clients
        
        # Check all providers are configured
        assert 'openai' in clients
        assert 'mistral' in clients
        assert 'deepseek' in clients
        
        # Check client structure
        for provider, config in clients.items():
            assert 'api_key' in config
            assert 'model' in config
            assert 'base_url' in config
            assert 'enabled' in config
    
    def test_get_available_providers(self, model_demos):
        """Test getting available providers"""
        providers = model_demos.get_available_providers()
        assert isinstance(providers, list)
        
        # Should include providers with valid API keys
        all_providers = ['openai', 'mistral', 'deepseek']
        for provider in providers:
            assert provider in all_providers
    
    def test_get_provider_status(self, model_demos):
        """Test getting provider status"""
        status = model_demos.get_provider_status()
        
        assert isinstance(status, dict)
        assert 'openai' in status
        assert 'mistral' in status
        assert 'deepseek' in status
        
        for provider, enabled in status.items():
            assert isinstance(enabled, bool)
    
    def test_rate_limiting(self, model_demos):
        """Test rate limiting functionality"""
        provider = 'openai'
        
        # Should allow initial requests
        assert model_demos.check_rate_limit(provider) is True
        
        # Simulate hitting rate limit
        with patch.dict(os.environ, {'DEMO_RATE_LIMIT': '2'}):
            # First two requests should pass
            assert model_demos.check_rate_limit(provider) is True
            assert model_demos.check_rate_limit(provider) is True
            
            # Third request should fail
            assert model_demos.check_rate_limit(provider) is False
    
    def test_legal_classifier(self, model_demos):
        """Test legal document classification"""
        test_text = "AI system for automated loan approval based on credit scoring"
        
        prediction, scores, explanation = model_demos.classify_document(test_text)
        
        assert prediction is not None
        assert isinstance(scores, dict)
        assert isinstance(explanation, str)
        assert len(scores) > 0
        
        # Check if prediction is valid risk level
        valid_risks = ['High Risk', 'Limited Risk', 'Minimal Risk']
        assert prediction in valid_risks or prediction == "Error"
    
    def test_classify_empty_text(self, model_demos):
        """Test classification with empty text"""
        prediction, scores, explanation = model_demos.classify_document("")
        
        assert prediction == "No text provided"
        assert scores == {}
        assert "Please enter text to classify" in explanation
    
    def test_feature_importance_chart(self, model_demos):
        """Test feature importance chart generation"""
        test_text = "AI system for customer service chatbot"
        
        fig = model_demos.create_feature_importance_chart(test_text)
        
        assert fig is not None
        # Should have some layout or data
        assert hasattr(fig, 'data') or hasattr(fig, 'layout')
    
    @patch('aiohttp.ClientSession.post')
    async def test_openai_api_call(self, mock_post, model_demos):
        """Test OpenAI API call"""
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Test response from OpenAI'}}]
        }
        mock_post.return_value.__aenter__.return_value = mock_response
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
            result = await model_demos.call_ai_model(
                'openai',
                'Test prompt',
                'Test system prompt'
            )
            
            assert result == 'Test response from OpenAI'
            mock_post.assert_called_once()
    
    @patch('aiohttp.ClientSession.post')
    async def test_mistral_api_call(self, mock_post, model_demos):
        """Test Mistral API call"""
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Test response from Mistral'}}]
        }
        mock_post.return_value.__aenter__.return_value = mock_response
        
        with patch.dict(os.environ, {'MISTRAL_API_KEY': 'test_key'}):
            result = await model_demos.call_ai_model(
                'mistral',
                'Test prompt',
                'Test system prompt'
            )
            
            assert result == 'Test response from Mistral'
            mock_post.assert_called_once()
    
    @patch('aiohttp.ClientSession.post')
    async def test_deepseek_api_call(self, mock_post, model_demos):
        """Test DeepSeek API call"""
        # Mock successful response
        mock_response = AsyncMock()
        mock_response.status = 200
        mock_response.json.return_value = {
            'choices': [{'message': {'content': 'Test response from DeepSeek'}}]
        }
        mock_post.return_value.__aenter__.return_value = mock_response
        
        with patch.dict(os.environ, {'DEEPSEEK_API_KEY': 'test_key'}):
            result = await model_demos.call_ai_model(
                'deepseek',
                'Test prompt',
                'Test system prompt'
            )
            
            assert result == 'Test response from DeepSeek'
            mock_post.assert_called_once()
    
    @patch('aiohttp.ClientSession.post')
    async def test_api_error_handling(self, mock_post, model_demos):
        """Test API error handling"""
        # Mock error response
        mock_response = AsyncMock()
        mock_response.status = 401
        mock_response.text.return_value = 'Unauthorized'
        mock_post.return_value.__aenter__.return_value = mock_response
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'invalid_key'}):
            result = await model_demos.call_ai_model('openai', 'Test prompt')
            
            assert 'API Error (401)' in result
            assert 'Unauthorized' in result
    
    @patch('aiohttp.ClientSession.post')
    async def test_api_timeout_handling(self, mock_post, model_demos):
        """Test API timeout handling"""
        # Mock timeout
        mock_post.side_effect = asyncio.TimeoutError()
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': 'test_key'}):
            result = await model_demos.call_ai_model('openai', 'Test prompt')
            
            assert 'Request timeout' in result
    
    def test_analyze_with_ai_governance(self, model_demos):
        """Test AI analysis with governance type"""
        test_text = "AI system for automated hiring decisions"
        
        with patch.object(model_demos, 'call_ai_model') as mock_call:
            mock_call.return_value = asyncio.Future()
            mock_call.return_value.set_result("High Risk - requires conformity assessment")
            
            result = model_demos.analyze_with_ai(test_text, 'openai', 'governance')
            
            assert 'High Risk' in result
            mock_call.assert_called_once()
    
    def test_analyze_with_ai_bias(self, model_demos):
        """Test AI analysis with bias detection"""
        test_text = "Resume screening algorithm showing gender disparities"
        
        with patch.object(model_demos, 'call_ai_model') as mock_call:
            mock_call.return_value = asyncio.Future()
            mock_call.return_value.set_result("Gender bias detected in hiring algorithm")
            
            result = model_demos.analyze_with_ai(test_text, 'mistral', 'bias')
            
            assert 'Gender bias' in result
            mock_call.assert_called_once()
    
    def test_analyze_with_ai_explainability(self, model_demos):
        """Test AI analysis with explainability type"""
        test_text = "Medical diagnosis AI system"
        
        with patch.object(model_demos, 'call_ai_model') as mock_call:
            mock_call.return_value = asyncio.Future()
            mock_call.return_value.set_result("Requires LIME and SHAP explanations")
            
            result = model_demos.analyze_with_ai(test_text, 'deepseek', 'explainability')
            
            assert 'explanations' in result
            mock_call.assert_called_once()
    
    def test_analyze_with_ai_disabled(self, model_demos):
        """Test AI analysis when demos are disabled"""
        test_text = "Test system"
        
        with patch.dict(os.environ, {'ENABLE_AI_DEMOS': 'false'}):
            result = model_demos.analyze_with_ai(test_text, 'openai', 'governance')
            
            assert 'AI demos are disabled' in result
    
    def test_analyze_with_ai_no_api_key(self, model_demos):
        """Test AI analysis with no API key"""
        test_text = "Test system"
        
        with patch.dict(os.environ, {'OPENAI_API_KEY': ''}):
            result = model_demos.analyze_with_ai(test_text, 'openai', 'governance')
            
            assert 'API key not configured' in result
    
    def test_create_provider_status_text(self, model_demos):
        """Test provider status text generation"""
        status_text = model_demos.create_provider_status_text()
        
        assert isinstance(status_text, str)
        assert '### 🔌 Provider Status' in status_text
        assert 'OpenAI' in status_text
        assert 'Mistral' in status_text
        assert 'DeepSeek' in status_text
    
    def test_sample_documents_loading(self, model_demos):
        """Test sample documents loading"""
        docs = model_demos.sample_documents
        
        assert isinstance(docs, list)
        assert len(docs) > 0
        
        # Check document content
        for doc in docs:
            assert isinstance(doc, str)
            assert len(doc) > 0

class TestModelDemosIntegration:
    """Integration tests for Model Demos with real API keys"""
    
    @pytest.fixture
    def model_demos_with_real_keys(self):
        """Create ModelDemos with real API keys from environment"""
        return ModelDemos()
    
    @pytest.mark.skipif(not os.getenv('OPENAI_API_KEY'), reason="OpenAI API key not available")
    def test_openai_integration(self, model_demos_with_real_keys):
        """Test OpenAI integration with real API"""
        test_text = "AI system for customer service automation"
        
        result = model_demos_with_real_keys.analyze_with_ai(test_text, 'openai', 'governance')
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert 'API Error' not in result
    
    @pytest.mark.skipif(not os.getenv('MISTRAL_API_KEY'), reason="Mistral API key not available")
    def test_mistral_integration(self, model_demos_with_real_keys):
        """Test Mistral integration with real API"""
        test_text = "Facial recognition system for building access"
        
        result = model_demos_with_real_keys.analyze_with_ai(test_text, 'mistral', 'bias')
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert 'API Error' not in result
    
    @pytest.mark.skipif(not os.getenv('DEEPSEEK_API_KEY'), reason="DeepSeek API key not available")
    def test_deepseek_integration(self, model_demos_with_real_keys):
        """Test DeepSeek integration with real API"""
        test_text = "Medical diagnosis AI requiring explanations"
        
        result = model_demos_with_real_keys.analyze_with_ai(test_text, 'deepseek', 'explainability')
        
        assert isinstance(result, str)
        assert len(result) > 0
        assert 'API Error' not in result

class TestModelDemosStress:
    """Stress tests for Model Demos component"""
    
    @pytest.fixture
    def model_demos(self):
        return ModelDemos()
    
    def test_multiple_classifications(self, model_demos):
        """Test multiple document classifications"""
        test_texts = [
            "AI system for loan approval",
            "Chatbot for customer service",
            "Facial recognition for security",
            "Product recommendation engine",
            "Automated resume screening"
        ]
        
        for text in test_texts:
            prediction, scores, explanation = model_demos.classify_document(text)
            
            assert prediction is not None
            assert isinstance(scores, dict)
            assert isinstance(explanation, str)
    
    def test_rate_limiting_stress(self, model_demos):
        """Test rate limiting under stress"""
        provider = 'test_provider'
        
        with patch.dict(os.environ, {'DEMO_RATE_LIMIT': '5'}):
            # Should allow up to 5 requests
            for i in range(5):
                assert model_demos.check_rate_limit(provider) is True
            
            # 6th request should fail
            assert model_demos.check_rate_limit(provider) is False
    
    def test_concurrent_requests(self, model_demos):
        """Test handling concurrent requests"""
        import threading
        
        results = []
        
        def classify_document():
            result = model_demos.classify_document("Test AI system")
            results.append(result)
        
        # Create multiple threads
        threads = []
        for i in range(5):
            thread = threading.Thread(target=classify_document)
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Check results
        assert len(results) == 5
        for result in results:
            assert result is not None
            assert len(result) == 3  # prediction, scores, explanation

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
