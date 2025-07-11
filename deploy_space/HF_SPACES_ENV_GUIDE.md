# 🔐 Hugging Face Spaces Environment Configuration Guide

## 🛡️ Secure Environment Variables for Hugging Face Spaces

### Option 1: Hugging Face Spaces Secrets (Recommended)
Hugging Face Spaces allows you to set environment variables securely through the web interface:

1. **Go to your Space**: https://huggingface.co/spaces/fartec0/ai-governance
2. **Click "Settings" tab**
3. **Scroll to "Repository secrets"**
4. **Add your API keys as secrets**:
   - `OPENAI_API_KEY`: Your OpenAI API key
   - `MISTRAL_API_KEY`: Your Mistral API key
   - `DEEPSEEK_API_KEY`: Your DeepSeek API key
   - `DEFAULT_MODEL_PROVIDER`: openai (or mistral/deepseek)
   - `ENABLE_AI_DEMOS`: true
   - `API_TIMEOUT`: 30
   - `MAX_TOKENS`: 2000
   - `TEMPERATURE`: 0.7
   - `DEMO_RATE_LIMIT`: 10

### Option 2: .env File (NOT for Production)
For local development only. Never commit .env files with real API keys.

### Option 3: Runtime Environment Detection
The app automatically detects if it's running in Spaces and adapts accordingly.

## 🔒 Security Best Practices

### ✅ DO:
- Use Hugging Face Spaces Secrets for API keys
- Set `ENABLE_AI_DEMOS=false` to disable features if no keys provided
- Use rate limiting to prevent API abuse
- Implement proper error handling for missing keys

### ❌ DON'T:
- Commit .env files with real API keys to git
- Hardcode API keys in source code
- Share API keys in public repositories
- Use development keys in production

## 🚀 Implementation Notes

The app is designed to:
1. **Gracefully degrade** when API keys are missing
2. **Show clear status** of available providers
3. **Provide setup instructions** when keys are not configured
4. **Respect rate limits** to prevent API abuse

## 🔧 Space Configuration Steps

1. **Add Secrets in Spaces UI**:
   ```
   OPENAI_API_KEY=your_actual_key_here
   MISTRAL_API_KEY=your_actual_key_here
   DEEPSEEK_API_KEY=your_actual_key_here
   DEFAULT_MODEL_PROVIDER=openai
   ENABLE_AI_DEMOS=true
   ```

2. **Restart the Space** to apply changes

3. **Verify in logs** that environment variables are loaded

## 🎯 Environment Detection Code

The app automatically detects the environment:
```python
# Check if running in Hugging Face Spaces
is_spaces = os.getenv("SPACE_ID") is not None

# Load environment variables
load_dotenv()  # This works for local .env files
# HF Spaces secrets are automatically available as os.environ
```

## 🔍 Status Checking

The Model Demos tab will show:
- ✅ **Available providers** (with API keys configured)
- ❌ **Unavailable providers** (missing API keys)
- ⚠️ **Setup instructions** when no providers are available

This ensures the app works for all users while providing enhanced features for those with API keys configured.
