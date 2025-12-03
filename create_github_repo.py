#!/usr/bin/env python3
"""
Automated GitHub Repository Creator
Creates a public GitHub repository using GitHub CLI or API
"""

import subprocess
import sys
import os

def run_command(cmd, capture_output=True):
    """Run a shell command and return output"""
    try:
        if capture_output:
            result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
            return result.returncode, result.stdout, result.stderr
        else:
            result = subprocess.run(cmd, shell=True)
            return result.returncode, "", ""
    except Exception as e:
        return 1, "", str(e)

def main():
    print("=" * 60)
    print("  GitHub Repository Creator - Item AI Assistant")
    print("=" * 60)
    print()
    
    repo_name = "item-ai-assistant"
    description = "Personal AI Assistant with voice control, desktop automation, and LLM integration"
    
    print("Repository Details:")
    print(f"  Name: {repo_name}")
    print(f"  Description: {description}")
    print(f"  Visibility: PUBLIC")
    print()
    
    # Check if GitHub CLI is installed
    print("Checking for GitHub CLI (gh)...")
    code, stdout, stderr = run_command("gh --version")
    
    if code != 0:
        print("❌ GitHub CLI not found!")
        print()
        print("Please install GitHub CLI from: https://cli.github.com/")
        print("Or create the repository manually:")
        print(f"  1. Go to: https://github.com/new")
        print(f"  2. Name: {repo_name}")
        print(f"  3. Description: {description}")
        print(f"  4. Visibility: Public")
        print(f"  5. Don't add README, .gitignore, or license")
        print(f"  6. Click 'Create repository'")
        print()
        input("Press Enter to exit...")
        return 1
    
    print(f"✓ GitHub CLI found: {stdout.split()[0]} {stdout.split()[2]}")
    print()
    
    # Check if authenticated
    print("Checking GitHub authentication...")
    code, stdout, stderr = run_command("gh auth status")
    
    if code != 0:
        print("❌ Not authenticated with GitHub!")
        print()
        print("Please run: gh auth login")
        print("Then run this script again.")
        print()
        input("Press Enter to exit...")
        return 1
    
    print("✓ Authenticated with GitHub")
    print()
    
    # Create repository
    print(f"Creating repository '{repo_name}'...")
    cmd = f'gh repo create {repo_name} --public --description "{description}" --source=. --remote=origin --push'
    
    print(f"Command: {cmd}")
    print()
    
    code, stdout, stderr = run_command(cmd, capture_output=False)
    
    if code == 0:
        print()
        print("=" * 60)
        print("  ✅ SUCCESS!")
        print("=" * 60)
        print()
        print(f"Repository created: https://github.com/$(gh api user --jq .login)/{repo_name}")
        print()
        print("Your Item AI Assistant is now public on GitHub!")
        print("You can share the repository URL with anyone.")
        print()
    else:
        print()
        print("❌ Failed to create repository")
        print("Error:", stderr)
        print()
        print("Please create the repository manually or check the error above.")
        print()
    
    input("Press Enter to exit...")
    return code

if __name__ == "__main__":
    sys.exit(main())
