#!/usr/bin/env python3
"""Max AI Agent — smart installer.

Detects the OS and installs the correct dependencies.
"""

import platform
import subprocess
import sys


def main():
    """Run the installer."""
    OS = platform.system()
    
    req_map = {
        "Windows": "requirements-windows.txt",
        "Darwin": "requirements-macos.txt",
        "Linux": "requirements-linux.txt",
    }
    
    req_file = req_map.get(OS)
    if not req_file:
        print(f"Unsupported OS: {OS}")
        sys.exit(1)
    
    print(f"Detected OS: {OS}")
    print(f"Installing from {req_file}...")
    
    try:
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", req_file
        ])
    except subprocess.CalledProcessError as e:
        print(f"Failed to install requirements: {e}")
        sys.exit(1)
    
    print("\nInstalling Playwright browsers...")
    try:
        subprocess.check_call([
            sys.executable, "-m", "playwright", "install", "chromium"
        ])
    except subprocess.CalledProcessError:
        print("Warning: Failed to install Playwright browsers")
    
    print("\nInstallation complete!")
    print("\nNext steps:")
    print("1. Copy .env.example to .env")
    print("2. Configure your LLM provider (local Ollama or cloud OpenRouter)")
    print("3. Run: python main.py")


if __name__ == "__main__":
    main()
