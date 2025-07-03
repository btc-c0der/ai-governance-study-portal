# 🚀 AI Governance Codex - Deployment Guide

## **Quick Fix for SSE Error**

The "SSE is not enabled" error when using `gradio deploy` is common. Here are **multiple solutions**:

## **🎯 Method 1: Smart Deployment Script (Recommended)**

Use our new deployment script that handles SSE issues automatically:

```bash
# Quick deployment
python deploy.py --space-name your-username/your-space-name

# Private space
python deploy.py --space-name your-username/your-space-name --private

# Use only Python API (bypasses CLI SSE issues)
python deploy.py --space-name your-username/your-space-name --method api
```

## **🔧 Method 2: Manual CLI with Fixes**

### Step 1: Update Gradio and Dependencies
```bash
pip install --upgrade gradio>=4.15.0 huggingface_hub>=0.20.0
```

### Step 2: Login to Hugging Face
```bash
huggingface-cli login
# or set environment variable:
export HF_TOKEN="your_token_here"
```

### Step 3: Deploy with Timeout
```bash
timeout 300 gradio deploy --timeout 300 --no-browser
```

## **🐍 Method 3: Python API Deployment**

If CLI keeps failing, use the Python API directly:

```python
from huggingface_hub import HfApi, create_repo

# Create space
create_repo(
    repo_id="your-username/space-name",
    repo_type="space",
    space_sdk="gradio",
    exist_ok=True
)

# Upload files
api = HfApi()
api.upload_folder(
    folder_path=".",
    repo_id="your-username/space-name",
    repo_type="space"
)
```

## **⚡ Method 4: GitHub Actions Auto-Deploy**

I've updated your `.github/workflows/update_space.yml` to handle SSE issues:

1. **Set up secrets in GitHub:**
   - Go to GitHub repo → Settings → Secrets
   - Add `HF_TOKEN` with your Hugging Face token

2. **Push to master branch:**
   ```bash
   git add .
   git commit -m "Deploy to Spaces"
   git push origin master
   ```

## **🔍 Troubleshooting SSE Issues**

### **Common Causes & Fixes:**

1. **Network/Firewall Issues:**
   ```bash
   # Try with VPN or different network
   # Check: curl -I https://huggingface.co
   ```

2. **Large Files:**
   ```bash
   # Set up Git LFS (already configured)
   git lfs install
   git lfs track "*.pdf" "*.db"
   git add .gitattributes
   ```

3. **Authentication Problems:**
   ```bash
   # Re-login
   huggingface-cli logout
   huggingface-cli login
   ```

4. **Gradio Version Conflicts:**
   ```bash
   # Clean reinstall
   pip uninstall gradio
   pip install gradio==4.15.0
   ```

## **📊 File Size Check**

Check for large files that might cause deployment issues:
```bash
find . -type f -size +50M -exec ls -lh {} \;
```

## **🆘 Emergency Deployment Method**

If all else fails, manual upload:

1. **Create space manually** on https://huggingface.co/new-space
2. **Clone the space:**
   ```bash
   git clone https://huggingface.co/spaces/your-username/space-name
   ```
3. **Copy files and push:**
   ```bash
   cp -r * /path/to/cloned/space/
   cd /path/to/cloned/space/
   git add .
   git commit -m "Initial upload"
   git push
   ```

## **🎯 Success Indicators**

✅ **Deployment Successful When You See:**
- "Space created successfully" or similar
- No timeout errors
- Gradio interface loads at the provided URL

❌ **Still Having Issues? Try:**
1. Different internet connection
2. VPN if in restricted region
3. Smaller batch uploads
4. Contact HF support: https://discuss.huggingface.co

## **📞 Quick Commands Summary**

```bash
# Option 1: Smart script
python deploy.py --space-name username/space-name

# Option 2: Direct CLI
gradio deploy --timeout 300

# Option 3: With retry
timeout 300 gradio deploy || (sleep 30 && timeout 300 gradio deploy)

# Option 4: Check auth
huggingface-cli whoami
```

---

💡 **Pro Tip:** The SSE error often resolves with a simple retry or network change. The smart deployment script handles this automatically! 