#!/usr/bin/env python3
"""
🚀 AI Governance Codex - Smart Deployment Script
Handles Gradio deployment with SSE error resolution and multiple deployment options.
"""

import os
import sys
import subprocess
import time
import argparse
from pathlib import Path

def check_huggingface_auth():
    """Check if Hugging Face authentication is set up"""
    try:
        import huggingface_hub
        
        # Check for token in environment
        token = os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_HUB_TOKEN")
        if token:
            print("✅ Found HF token in environment")
            return token
            
        # Check if already logged in
        try:
            user_info = huggingface_hub.whoami()
            print(f"✅ Already logged in as: {user_info['name']}")
            return True
        except:
            print("❌ Not logged in to Hugging Face")
            return False
            
    except ImportError:
        print("❌ huggingface_hub not installed")
        return False

def install_deployment_deps():
    """Install deployment dependencies"""
    deps = ["gradio>=4.15.0", "huggingface_hub>=0.20.0"]
    
    print("📦 Installing deployment dependencies...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + deps)
        print("✅ Dependencies installed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def prepare_for_deployment():
    """Prepare application for deployment"""
    print("🔧 Preparing for deployment...")
    
    # Check for large files that might cause issues
    large_files = []
    for root, dirs, files in os.walk("."):
        for file in files:
            filepath = Path(root) / file
            if filepath.stat().st_size > 50 * 1024 * 1024:  # 50MB
                large_files.append(filepath)
    
    if large_files:
        print("⚠️  Warning: Large files detected:")
        for file in large_files:
            size_mb = file.stat().st_size / (1024 * 1024)
            print(f"   📄 {file}: {size_mb:.1f} MB")
        print("   Consider using Git LFS or reducing file sizes")
    
    # Create/update .gitattributes for LFS
    gitattributes_content = """
*.pdf filter=lfs diff=lfs merge=lfs -text
*.db filter=lfs diff=lfs merge=lfs -text
*.sqlite filter=lfs diff=lfs merge=lfs -text
*.json filter=lfs diff=lfs merge=lfs -text
*.pkl filter=lfs diff=lfs merge=lfs -text
*.bin filter=lfs diff=lfs merge=lfs -text
"""
    
    with open(".gitattributes", "w") as f:
        f.write(gitattributes_content.strip())
    
    print("✅ Deployment preparation complete")

def deploy_to_spaces_cli(space_name=None, private=False):
    """Deploy using Gradio CLI with SSE error handling"""
    print("🚀 Deploying to Hugging Face Spaces using CLI...")
    
    # Build gradio deploy command
    cmd = ["gradio", "deploy"]
    
    if space_name:
        cmd.extend(["--space-name", space_name])
    
    if private:
        cmd.append("--private")
    
    # Add SSE-related flags
    cmd.extend([
        "--timeout", "300",  # 5 minute timeout
        "--no-browser",      # Don't open browser
    ])
    
    max_retries = 3
    for attempt in range(max_retries):
        try:
            print(f"📡 Deployment attempt {attempt + 1}/{max_retries}")
            
            # Run with timeout
            result = subprocess.run(
                cmd,
                timeout=600,  # 10 minute timeout
                capture_output=True,
                text=True
            )
            
            if result.returncode == 0:
                print("✅ Deployment successful!")
                print(result.stdout)
                return True
            else:
                print(f"❌ Deployment failed with return code {result.returncode}")
                print("STDOUT:", result.stdout)
                print("STDERR:", result.stderr)
                
        except subprocess.TimeoutExpired:
            print(f"⏰ Deployment attempt {attempt + 1} timed out")
            
        except Exception as e:
            print(f"💥 Deployment attempt {attempt + 1} failed: {e}")
        
        if attempt < max_retries - 1:
            wait_time = (attempt + 1) * 30  # Exponential backoff
            print(f"⏳ Waiting {wait_time} seconds before retry...")
            time.sleep(wait_time)
    
    print("💔 All deployment attempts failed")
    return False

def deploy_with_python_api(space_name, private=False):
    """Deploy using Python API as alternative"""
    print("🐍 Trying deployment with Python API...")
    
    try:
        from huggingface_hub import HfApi, create_repo
        
        api = HfApi()
        
        # Create repo if it doesn't exist
        try:
            repo_url = create_repo(
                repo_id=space_name,
                repo_type="space",
                space_sdk="gradio",
                private=private,
                exist_ok=True
            )
            print(f"✅ Space created/verified: {repo_url}")
        except Exception as e:
            print(f"⚠️  Repo creation warning: {e}")
        
        # Upload files
        api.upload_folder(
            folder_path=".",
            repo_id=space_name,
            repo_type="space",
            ignore_patterns=[".git", "__pycache__", "*.pyc", ".DS_Store"]
        )
        
        print("✅ Files uploaded successfully!")
        print(f"🌐 Your space: https://huggingface.co/spaces/{space_name}")
        return True
        
    except Exception as e:
        print(f"❌ Python API deployment failed: {e}")
        return False

def main():
    parser = argparse.ArgumentParser(description="Deploy AI Governance Codex to Hugging Face Spaces")
    parser.add_argument("--space-name", help="Name of the Hugging Face Space")
    parser.add_argument("--private", action="store_true", help="Create private space")
    parser.add_argument("--method", choices=["cli", "api", "both"], default="both", 
                       help="Deployment method")
    
    args = parser.parse_args()
    
    print("🧠⚖️ AI Governance Codex - Deployment Script")
    print("=" * 50)
    
    # Install dependencies
    if not install_deployment_deps():
        sys.exit(1)
    
    # Check authentication
    if not check_huggingface_auth():
        print("💡 Please log in to Hugging Face:")
        print("   huggingface-cli login")
        print("   or set HF_TOKEN environment variable")
        sys.exit(1)
    
    # Prepare for deployment
    prepare_for_deployment()
    
    # Determine space name
    space_name = args.space_name
    if not space_name:
        space_name = input("Enter your Hugging Face Space name (username/space-name): ").strip()
        if not space_name:
            print("❌ Space name is required")
            sys.exit(1)
    
    # Try deployment methods
    success = False
    
    if args.method in ["cli", "both"]:
        print("\n🚀 Method 1: Gradio CLI Deployment")
        success = deploy_to_spaces_cli(space_name, args.private)
    
    if not success and args.method in ["api", "both"]:
        print("\n🚀 Method 2: Python API Deployment")
        success = deploy_with_python_api(space_name, args.private)
    
    if success:
        print("\n🎉 Deployment completed successfully!")
        print(f"🌐 Access your space at: https://huggingface.co/spaces/{space_name}")
    else:
        print("\n💔 Deployment failed with all methods")
        print("\n💡 Troubleshooting tips:")
        print("1. Check your internet connection")
        print("2. Verify Hugging Face authentication")
        print("3. Ensure space name is available")
        print("4. Try reducing file sizes")
        print("5. Check Hugging Face status: https://status.huggingface.co/")
        sys.exit(1)

if __name__ == "__main__":
    main() 