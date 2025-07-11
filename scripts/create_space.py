from huggingface_hub import HfApi
import os

# Initialize the Hugging Face API client
api = HfApi()

# Create the Space
try:
    space_info = api.create_repo(
        repo_id="ai-governance-codex",
        repo_type="space",
        space_sdk="gradio"
    )
    print(f"✅ Space created successfully: {space_info}")
except Exception as e:
    print(f"Note: {e}")
    print("Continuing with upload...")

# Upload the deployment folder
api.upload_folder(
    folder_path="deploy_space",
    repo_id=f"{api.whoami()['name']}/ai-governance-codex",
    repo_type="space"
)

print("✅ Deployment completed! Your space will be available at:")
print(f"https://huggingface.co/spaces/{api.whoami()['name']}/ai-governance-codex") 