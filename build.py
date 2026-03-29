#!/usr/bin/env python3
"""Max AI Agent — build script.

Creates a distributable executable for the current OS.
"""

import platform
import shutil
import subprocess
import sys
from pathlib import Path


OS = platform.system()
BUILD_DIR = Path("dist")


def clean():
    """Clean build artifacts."""
    for d in ["build", "dist", "__pycache__"]:
        shutil.rmtree(d, ignore_errors=True)
    print("Cleaned.")


def build():
    """Build the executable."""
    cmd = [
        "pyinstaller",
        "--name=MaxAIAgent",
        "--windowed",
        "--onedir",
        "--add-data=data:data",
        "--add-data=.env.example:.env.example",
        "--hidden-import=PyQt6",
        "--hidden-import=faster_whisper",
        "--hidden-import=easyocr",
        "main.py",
    ]

    if OS == "Windows":
        cmd += ["--icon=assets/icon.ico"]
    elif OS == "Darwin":
        cmd += ["--osx-bundle-identifier=com.max.aiagent"]
    elif OS == "Linux":
        cmd += ["--icon=assets/icon.png"]

    subprocess.check_call(cmd)
    print(f"\nBuild complete. Output in: {BUILD_DIR}/MaxAIAgent/")


def main():
    """Main entry point."""
    if "--clean" in sys.argv:
        clean()
    
    build()


if __name__ == "__main__":
    main()
