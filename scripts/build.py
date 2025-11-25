#!/usr/bin/env python3
"""
Unified build script for FaceSwap application.
Handles installation, testing, and packaging.
"""

import sys
import subprocess
import argparse
import os
from pathlib import Path

def run_command(cmd, description=""):
    """Run a command and return success status."""
    if description:
        print(f"[INFO] {description}")
    
    print(f"[CMD] {' '.join(cmd)}")
    try:
        result = subprocess.run(cmd, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"[ERROR] Command failed: {e}")
        return False

def install_dependencies():
    """Install Python dependencies."""
    return run_command([
        sys.executable, "-m", "pip", "install", 
        "-r", "requirements.txt"
    ], "Installing dependencies")

def download_models():
    """Download AI models."""
    return run_command([
        sys.executable, "download_models.py"
    ], "Downloading AI models")

def run_tests():
    """Run test suite."""
    return run_command([
        sys.executable, "run_tests.py", "--quick"
    ], "Running tests")

def main():
    parser = argparse.ArgumentParser(description="FaceSwap Build Tool")
    parser.add_argument("command", choices=[
        "setup", "install", "models", "test", "run"
    ], help="Command to execute")
    
    args = parser.parse_args()
    
    if args.command == "setup":
        print("=== FaceSwap Setup ===")
        success = (
            install_dependencies() and
            download_models() and
            run_tests()
        )
        if success:
            print("✅ Setup complete! Run: python main.py")
            return 0
        else:
            print("❌ Setup failed!")
            return 1
    
    elif args.command == "install":
        return 0 if install_dependencies() else 1
    
    elif args.command == "models":
        return 0 if download_models() else 1
    
    elif args.command == "test":
        return 0 if run_tests() else 1
    
    elif args.command == "run":
        return 0 if run_command([sys.executable, "main.py"]) else 1

if __name__ == "__main__":
    sys.exit(main())
