#!/usr/bin/env python3
"""
Development setup script for FaceSwap application.
Checks dependencies, downloads models, and verifies setup.
"""

import os
import sys
import subprocess
import importlib
from pathlib import Path

def check_python_version():
    """Check Python version compatibility."""
    version = sys.version_info
    if version < (3, 8):
        print(f"❌ Python {version.major}.{version.minor} detected. Python 3.8+ required.")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro}")
    return True

def check_package(package_name, import_name=None):
    """Check if a package is installed."""
    if import_name is None:
        import_name = package_name
    
    try:
        importlib.import_module(import_name)
        print(f"✅ {package_name}")
        return True
    except ImportError:
        print(f"❌ {package_name} - not installed")
        return False

def check_models():
    """Check if model files are available."""
    models_dir = Path("models")
    model_file = models_dir / "shape_predictor_68_face_landmarks.dat"
    
    if model_file.exists() and model_file.stat().st_size > 1000000:
        print(f"✅ Model files present ({model_file.stat().st_size // (1024*1024)}MB)")
        return True
    else:
        print("❌ Model files missing or incomplete")
        return False

def run_setup():
    """Run the complete setup process."""
    print("FaceSwap Development Setup")
    print("=" * 30)
    
    # Check Python version
    if not check_python_version():
        return False
    
    print("\nChecking dependencies...")
    dependencies = [
        ("opencv-python", "cv2"),
        ("numpy", "numpy"),
        ("PySide6", "PySide6"),
        ("dlib", "dlib"),
        ("pytest", "pytest"),
    ]
    
    all_deps_ok = True
    for package_name, import_name in dependencies:
        if not check_package(package_name, import_name):
            all_deps_ok = False
    
    if not all_deps_ok:
        print("\n❌ Some dependencies are missing. Install with:")
        print("pip install -r requirements.txt")
        return False
    
    print("\nChecking model files...")
    if not check_models():
        print("\n📥 Downloading model files...")
        try:
            result = subprocess.run(["./setup_models.sh"], check=True, capture_output=True, text=True)
            print("✅ Model files downloaded successfully")
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to download models: {e}")
            return False
    
    print("\n🧪 Running basic tests...")
    try:
        result = subprocess.run(["python", "-m", "pytest", "tests/test_installation.py", "-v"], 
                              capture_output=True, text=True, check=True)
        print("✅ Installation tests passed")
    except subprocess.CalledProcessError as e:
        print(f"❌ Some tests failed: {e}")
        print("Output:", e.stdout)
        return False
    
    print("\n🎉 Setup complete! Ready for development.")
    print("\nNext steps:")
    print("- Run 'python -m pytest -v' to run all tests")
    print("- Run 'python main.py' to start the GUI application")
    return True

if __name__ == "__main__":
    success = run_setup()
    sys.exit(0 if success else 1)
