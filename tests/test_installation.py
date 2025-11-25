import pytest
import sys
import os
from pathlib import Path

class TestInstallation:
    """Test installation and dependencies."""
    
    def test_python_version(self):
        """Test Python version compatibility."""
        assert sys.version_info >= (3, 8), f"Python 3.8+ required, got {sys.version_info[:2]}"
    
    def test_opencv_import(self):
        """Test OpenCV import and basic functionality."""
        import cv2
        # Test basic functionality
        img = cv2.imread('nonexistent.jpg')  # Should return None
        assert img is None
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        assert fourcc is not None
    
    def test_numpy_import(self):
        """Test NumPy import and functionality."""
        import numpy as np
        arr = np.array([1, 2, 3])
        assert arr.sum() == 6
    
    def test_pyside6_import(self):
        """Test PySide6 import."""
        try:
            from PySide6 import QtCore, QtGui, QtWidgets
            assert QtCore is not None
        except ImportError:
            pytest.skip("PySide6 not available")
    
    def test_dlib_import(self):
        """Test Dlib import."""
        try:
            import dlib
            detector = dlib.get_frontal_face_detector()
            assert detector is not None
        except ImportError:
            pytest.skip("Dlib not available")
    
    def test_model_files(self):
        """Test that required model files are present."""
        models_dir = "models"
        required_models = [
            "shape_predictor_68_face_landmarks.dat"
        ]
        
        if not os.path.exists(models_dir):
            pytest.skip(f"Models directory '{models_dir}' does not exist. Run setup_models.sh to download.")
        
        missing_models = []
        for model_file in required_models:
            model_path = os.path.join(models_dir, model_file)
            if not os.path.exists(model_path):
                missing_models.append(model_file)
            else:
                # Check file size to ensure it's not empty/corrupted
                file_size = os.path.getsize(model_path)
                if file_size < 1000000:  # Should be > 1MB
                    missing_models.append(f"{model_file} (file too small: {file_size} bytes)")
        
        if missing_models:
            pytest.skip(f"Missing or invalid model files: {missing_models}. Run './setup_models.sh' to download.")
        
        # All models present and valid
        assert True

    def test_core_modules_import(self):
        """Test core application modules can be imported."""
        # Test config
        try:
            import config
            assert hasattr(config, 'APP_NAME')
        except ImportError:
            pytest.fail("Cannot import config module")
        
        # Test utils
        try:
            from utils.video_utils import VideoUtils
            from utils.smoothing import EMA
        except ImportError:
            pytest.fail("Cannot import utils modules")
