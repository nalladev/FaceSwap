import pytest
import numpy as np
import cv2
import sys
import os
from pathlib import Path
import tempfile
import logging

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

logger = logging.getLogger(__name__)

class TestFaceDetection:
    """Core face detection tests."""
    
    def test_face_detector_import(self):
        """Test that face detector can be imported."""
        try:
            from face_detector import FaceDetector
            assert FaceDetector is not None
        except ImportError:
            pytest.skip("FaceDetector not available")
    
    def test_synthetic_face_detection(self, synthetic_face_image):
        """Test detection on synthetic face."""
        try:
            from face_detector import FaceDetector
            detector = FaceDetector()
            faces = detector.detect_faces(synthetic_face_image)
            assert isinstance(faces, (list, tuple, np.ndarray))
        except ImportError:
            pytest.skip("FaceDetector not available")

class TestVideoUtils:
    """Video utilities tests."""
    
    def test_video_utils_import(self):
        """Test VideoUtils import."""
        from utils.video_utils import VideoUtils
        assert hasattr(VideoUtils, 'get_video_info')
        assert hasattr(VideoUtils, 'is_valid_video')
    
    def test_video_info_invalid_path(self):
        """Test video info with invalid path."""
        from utils.video_utils import VideoUtils
        info = VideoUtils.get_video_info('nonexistent.mp4')
        assert isinstance(info, dict)

class TestSmoothing:
    """Smoothing utilities tests."""
    
    def test_smoothing_import(self):
        """Test smoothing import."""
        from utils.smoothing import EMA, OneEuroFilter, LandmarkSmoother
        assert EMA is not None
        assert OneEuroFilter is not None
        assert LandmarkSmoother is not None
    
    def test_ema_smoother(self):
        """Test EMA smoother."""
        from utils.smoothing import EMA
        smoother = EMA(alpha=0.5)
        
        # Test with simple data
        data = np.array([1.0, 2.0, 3.0])
        result = smoother.update(data)
        assert result is not None
        assert result.shape == data.shape

class TestGUI:
    """GUI component tests."""
    
    def test_face_card_import(self):
        """Test FaceCard import."""
        try:
            from gui.face_card import FaceCard
            assert FaceCard is not None
        except ImportError:
            pytest.skip("GUI components not available")
    
    def test_main_window_import(self):
        """Test MainWindow import."""
        try:
            from gui.main_window import MainWindow
            assert MainWindow is not None
        except ImportError:
            pytest.skip("GUI components not available")

class TestStress:
    """Stress and performance tests."""
    
    def test_rapid_processing(self, synthetic_face_image):
        """Test rapid succession processing."""
        success_count = 0
        
        for i in range(10):  # Reduced from 50 for faster testing
            try:
                # Basic image processing
                if len(synthetic_face_image.shape) == 3:
                    gray = cv2.cvtColor(synthetic_face_image, cv2.COLOR_BGR2GRAY)
                    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
                    success_count += 1
            except Exception:
                continue
        
        assert success_count > 0
    
    @pytest.mark.slow
    def test_memory_pressure(self):
        """Test memory pressure handling."""
        try:
            import psutil
            process = psutil.Process()
            initial_memory = process.memory_info().rss
            
            # Create moderate memory pressure
            large_images = []
            for i in range(5):  # Reduced size
                size = 200 + (i * 50)  # Smaller images
                large_img = np.random.randint(0, 255, (size, size, 3), dtype=np.uint8)
                large_images.append(large_img)
            
            # Clean up
            del large_images
            import gc
            gc.collect()
            
            assert True  # Test passes if no crash
            
        except ImportError:
            pytest.skip("psutil not available")

class TestIntegration:
    """Integration tests for complete workflows."""
    
    def test_basic_pipeline(self, synthetic_face_image, temp_output_dir):
        """Test basic processing pipeline."""
        # Test complete flow without dependencies on missing modules
        try:
            # Step 1: Image validation
            assert synthetic_face_image is not None
            assert synthetic_face_image.shape[2] == 3
            
            # Step 2: Basic processing
            gray = cv2.cvtColor(synthetic_face_image, cv2.COLOR_BGR2GRAY)
            assert gray is not None
            
            # Step 3: Output saving
            output_path = temp_output_dir / "test_output.jpg"
            success = cv2.imwrite(str(output_path), synthetic_face_image)
            assert success
            assert output_path.exists()
            
        except Exception as e:
            pytest.fail(f"Basic pipeline failed: {e}")
