# AI Governance Architect's Codex - Version Tags

This document tracks important version tags in the repository.

## v1.0.0-spaces-working (July 12, 2025)

This tag marks a stable version of the application that successfully deploys to Hugging Face Spaces.

### Key Features:
- Fixed Gradio schema parsing issues with `gradio_patch.py`
- Created robust deployment with fallback mechanisms
- Enhanced `app_hf.py` as the primary entry point for Spaces
- Updated requirements to use Gradio 5.36.0+
- Added resilient error handling for deployment edge cases

### Deployment Instructions:
1. Navigate to the `deploy_space` directory
2. Run `./deploy.sh` to deploy to Hugging Face Spaces
3. The script will automatically try multiple entry points if needed

### Fallback Options:
- `app_hf.py`: Primary entry point with patched Gradio
- `app_safe.py`: Minimal version that avoids schema issues
- `app.py`: Standard app version

### Testing:
Local testing confirms the app works on port 7860 without schema errors.
