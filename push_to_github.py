#!/usr/bin/env python3
"""Simple git push script to handle GitHub sync."""

import subprocess
import os
import sys

def run_command(cmd, description):
    """Run a git command and handle output."""
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"Command: {' '.join(cmd)}")
    print(f"{'='*60}")
    
    try:
        result = subprocess.run(
            cmd,
            cwd=r"C:\Users\30reh\Downloads\voice",
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.stdout:
            print("STDOUT:")
            print(result.stdout)
        if result.stderr:
            print("STDERR:")
            print(result.stderr)
        
        return result.returncode == 0
    except subprocess.TimeoutExpired:
        print("ERROR: Command timed out")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def main():
    """Main push workflow."""
    os.chdir(r"C:\Users\30reh\Downloads\voice")
    
    # 1. Check status
    run_command(["git", "status"], "Checking git status...")
    
    # 2. Fetch from remote
    success = run_command(["git", "fetch", "origin", "main"], "Fetching from origin...")
    if not success:
        print("Fetch failed!")
        return False
    
    # 3. Rebase with remote
    success = run_command(["git", "rebase", "origin/main"], "Rebasing with remote...")
    if not success:
        print("Rebase failed - trying merge instead...")
        run_command(["git", "merge", "origin/main", "-m", "Merge remote changes"], "Merging remote changes...")
    
    # 4. Push to GitHub
    success = run_command(["git", "push", "-u", "origin", "main"], "Pushing to GitHub...")
    if success:
        print("\n" + "="*60)
        print("✅ SUCCESS! Code pushed to GitHub")
        print("="*60)
        return True
    else:
        print("\n" + "="*60)
        print("❌ FAILED! Push encountered an error")
        print("="*60)
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
