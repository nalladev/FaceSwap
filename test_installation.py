#!/usr/bin/env python3
"""
Installation Test Script for FaceSwap

This script validates that all required dependencies are installed
and working properly before building the application.

Usage:
    python test_installation.py

Returns:
    0 - All tests passed
    1 - One or more tests failed
"""

import sys
import traceback
import os
from pathlib import Path

# Test results tracking
tests_passed = 0
tests_failed = 0
critical_failures = []

def test_info(message):
    print(f"[INFO] {message}")

def test_pass(test_name):
    global tests_passed
    tests_passed += 1
    print(f"[PASS] {test_name}")

def test_fail(test_name, error=None):
    global tests_failed, critical_failures
    tests_failed += 1
    print(f"[FAIL] {test_name}")
    if error:
        print(f"       Error: {error}")
        critical_failures.append(f"{test_name}: {error}")

def test_python_version():
    """Test Python version compatibility."""
    version = sys.version_info
    if version >= (3, 8):
        test_pass(f"Python version {version.major}.{version.minor}.{version.micro}")
        return True
    else:
        test_fail(f"Python version {version.major}.{version.minor}.{version.micro} (requires 3.8+)")
        return False

def test_import_numpy():
    """Test NumPy import and basic functionality."""
    try:
        import numpy as np
        # Test basic functionality
        arr = np.array([1, 2, 3])
        assert arr.sum() == 6
        test_pass(f"NumPy {np.__version__}")
        return True
    except ImportError as e:
        test_fail("NumPy import", str(e))
        return False
    except Exception as e:
        test_fail("NumPy functionality", str(e))
        return False

def test_import_pillow():
    """Test Pillow/PIL import and basic functionality."""
    try:
        from PIL import Image
        import PIL
        # Test basic functionality
        img = Image.new('RGB', (10, 10), color='red')
        assert img.size == (10, 10)
        test_pass(f"Pillow {PIL.__version__}")
        return True
    except ImportError as e:
        test_fail("Pillow import", str(e))
        return False
    except Exception as e:
        test_fail("Pillow functionality", str(e))
        return False

def test_import_opencv():
    """Test OpenCV import and basic functionality."""
    try:
        import cv2
        # Test basic functionality
        img = cv2.imread('nonexistent.jpg')  # Should return None, not crash
        assert img is None
        # Test video codec availability
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        assert fourcc is not None
        test_pass(f"OpenCV {cv2.__version__}")
        return True
    except ImportError as e:
        test_fail("OpenCV import", str(e))
        return False
    except Exception as e:
        test_fail("OpenCV functionality", str(e))
        return False

def test_import_dlib():
    """Test Dlib import and basic functionality."""
    try:
        import dlib
        # Test face detector creation (doesn't require model files)
        detector = dlib.get_frontal_face_detector()
        assert detector is not None
        test_pass(f"Dlib {dlib.__version__}")
        return True
    except ImportError as e:
        test_fail("Dlib import", str(e))
        return False
    except Exception as e:
        test_fail("Dlib functionality", str(e))
        return False

def test_import_pyside6():
    """Test PySide6 import and basic functionality."""
    try:
        from PySide6 import QtCore, QtGui, QtWidgets
        # Test version
        version = QtCore.__version__
        # Test basic functionality
        app = QtWidgets.QApplication.instance()
        if app is None:
            # Create minimal app for testing
            import sys
            app = QtWidgets.QApplication(sys.argv)
        
        widget = QtWidgets.QWidget()
        assert widget is not None
        test_pass(f"PySide6 {version}")
        return True
    except ImportError as e:
        test_fail("PySide6 import", str(e))
        return False
    except Exception as e:
        test_fail("PySide6 functionality", str(e))
        return False

def test_model_files():
    """Test that required model files exist."""
    models_dir = Path("models")
    required_models = [
        "shape_predictor_68_face_landmarks.dat",
        "dlib_face_recognition_resnet_model_v1.dat"
    ]
    
    if not models_dir.exists():
        test_fail("Models directory missing")
        return False
    
    all_models_present = True
    for model_file in required_models:
        model_path = models_dir / model_file
        if model_path.exists():
            size_mb = model_path.stat().st_size / (1024 * 1024)
            test_pass(f"Model file: {model_file} ({size_mb:.1f}MB)")
        else:
            test_fail(f"Model file missing: {model_file}")
            all_models_present = False
    
    return all_models_present

def test_core_modules():
    """Test that our core application modules can be imported."""
    try:
        # Test face detector
        from face_detector import FaceDetector
        test_pass("FaceDetector module import")
        
        # Test face swapper
        from face_swapper import FaceSwapper  
        test_pass("FaceSwapper module import")
        
        # Test GUI modules
        from gui.main_window import MainWindow
        test_pass("MainWindow module import")
        
        from gui.face_card import FaceCard
        test_pass("FaceCard module import")
        
        from gui.progress_dialog import ProgressDialog
        test_pass("ProgressDialog module import")
        
        return True
    except ImportError as e:
        test_fail("Core module import", str(e))
        return False
    except Exception as e:
        test_fail("Core module functionality", str(e))
        return False

def test_face_detector_initialization():
    """Test that FaceDetector can be initialized with model files."""
    try:
        from face_detector import FaceDetector
        detector = FaceDetector()
        test_pass("FaceDetector initialization")
        return True
    except Exception as e:
        test_fail("FaceDetector initialization", str(e))
        return False

def test_system_resources():
    """Test system resources and requirements."""
    try:
        import psutil
        
        # Check available memory
        memory = psutil.virtual_memory()
        memory_gb = memory.total / (1024**3)
        
        if memory_gb >= 4.0:
            test_pass(f"System memory: {memory_gb:.1f}GB")
        else:
            test_fail(f"Insufficient memory: {memory_gb:.1f}GB (4GB+ recommended)")
        
        # Check CPU cores
        cpu_count = psutil.cpu_count()
        if cpu_count >= 2:
            test_pass(f"CPU cores: {cpu_count}")
        else:
            test_fail(f"Limited CPU cores: {cpu_count} (2+ recommended)")
            
        return True
    except ImportError:
        test_info("psutil not available, skipping system resource checks")
        return True
    except Exception as e:
        test_fail("System resource check", str(e))
        return False

def main():
    """Run all installation tests."""
    print("=" * 60)
    print("  FaceSwap Installation Test Suite")
    print("=" * 60)
    print()
    
    # Core Python tests
    test_info("Testing Python environment...")
    test_python_version()
    
    # Dependency tests
    test_info("Testing Python dependencies...")
    test_import_numpy()
    test_import_pillow()
    test_import_opencv()
    test_import_dlib()
    test_import_pyside6()
    
    # Model file tests
    test_info("Testing model files...")
    test_model_files()
    
    # Application module tests
    test_info("Testing application modules...")
    test_core_modules()
    test_face_detector_initialization()
    
    # System resource tests
    test_info("Testing system resources...")
    test_system_resources()
    
    # Summary
    print()
    print("=" * 60)
    print("  Test Results Summary")
    print("=" * 60)
    print(f"Tests passed: {tests_passed}")
    print(f"Tests failed: {tests_failed}")
    print()
    
    if tests_failed == 0:
        print("🎉 ALL TESTS PASSED! 🎉")
        print("Your installation is ready for building.")
        return 0
    else:
        print("❌ SOME TESTS FAILED ❌")
        print()
        print("Critical failures:")
        for failure in critical_failures:
            print(f"  • {failure}")
        print()
        print("Please fix these issues before building the application.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\nTest interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error during testing: {e}")
        traceback.print_exc()
        sys.exit(1)