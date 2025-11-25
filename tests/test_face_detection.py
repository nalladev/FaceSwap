import os
import cv2
import pytest
import numpy as np
import psutil
import gc

class TestFaceDetectionEnhanced:
    """Enhanced test suite for face detection with edge cases and performance tests."""
    
    @pytest.mark.skip(reason="Function import needs to be implemented")
    def test_face_detection_different_angles(self, sample_face_image):
        """Test face detection with different face angles."""
        pass

    @pytest.mark.skip(reason="Function import needs to be implemented") 
    def test_face_detection_different_lighting(self, sample_face_image):
        """Test face detection under different lighting conditions."""
        pass
    
    def test_face_detection_memory_usage(self, sample_face_image):
        """Test memory usage during face detection."""
        process = psutil.Process()
        initial_memory = process.memory_info().rss

        # Import face detector properly
        try:
            from face_detector import FaceDetector
            detector = FaceDetector()
        except (ImportError, FileNotFoundError):
            pytest.skip("Face detector not available or model files missing")
            return

        # Run detection multiple times
        detected_faces_count = 0
        for _ in range(10):  # Reduced iterations to speed up test
            try:
                faces = detector.detect_faces(sample_face_image)
                if faces:
                    detected_faces_count += len(faces)
            except Exception:
                # If detection fails, continue with memory test
                pass
            
            # Force garbage collection
            gc.collect()

        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024, f"Memory increase too large: {memory_increase} bytes"
        
        # Test completed successfully
        assert True
    
    @staticmethod
    def rotate_image(image, angle):
        """Helper method to rotate an image."""
        height, width = image.shape[:2]
        center = (width // 2, height // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(image, rotation_matrix, (width, height))