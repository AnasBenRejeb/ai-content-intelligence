#!/usr/bin/env python3
"""
Trigger GitHub Actions workflow
Requires: pip install requests
"""
import requests
import os
import sys

# You need to create a GitHub Personal Access Token
# Go to: https://github.com/settings/tokens
# Create token with 'workflow' scope
GITHUB_TOKEN = os.environ.get('GITHUB_TOKEN', '')

if not GITHUB_TOKEN:
    print("❌ Error: GITHUB_TOKEN environment variable not set")
    print("\nTo create a token:")
    print("1. Go to https://github.com/settings/tokens")
    print("2. Click 'Generate new token (classic)'")
    print("3. Select 'workflow' scope")
    print("4. Copy the token")
    print("5. Set it: $env:GITHUB_TOKEN='your_token_here'")
    sys.exit(1)

url = "https://api.github.com/repos/AnasBenRejeb/ai-content-intelligence/actions/workflows/generate-articles-simple.yml/dispatches"

headers = {
    "Accept": "application/vnd.github.v3+json",
    "Authorization": f"token {GITHUB_TOKEN}"
}

data = {
    "ref": "main"
}

print("🚀 Triggering workflow...")
response = requests.post(url, headers=headers, json=data)

if response.status_code == 204:
    print("✅ Workflow triggered successfully!")
    print("📊 Check status: https://github.com/AnasBenRejeb/ai-content-intelligence/actions")
else:
    print(f"❌ Failed: {response.status_code}")
    print(response.text)
