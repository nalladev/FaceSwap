import os
import cv2
import pytest
from face_detection_module import detect_faces  # Adjust the import based on your project structure

# Assuming the existence of a fixture that provides a sample face image for testing
@pytest.fixture
def sample_face_image():
    image_path = os.path.join(os.path.dirname(__file__), "test_images", "sample_face.jpg")
    return cv2.imread(image_path)

class TestFaceDetectionEnhanced:
    """Enhanced test suite for face detection with edge cases and performance tests."""
    
    def test_face_detection_different_angles(self, test_data_dir):
        """Test face detection with faces at different angles."""
        # Test rotated face images
        base_image = cv2.imread(os.path.join(test_data_dir, "single_face.jpg"))
        for angle in [15, 30, 45, -15, -30]:
            rotated = self.rotate_image(base_image, angle)
            faces = detect_faces(rotated)
            assert isinstance(faces, list), f"Failed to detect faces at {angle} degrees"
    
    def test_face_detection_different_lighting(self, sample_face_image):
        """Test face detection under different lighting conditions."""
        # Dark image
        dark_image = cv2.convertScaleAbs(sample_face_image, alpha=0.3, beta=0)
        faces_dark = detect_faces(dark_image)
        
        # Bright image
        bright_image = cv2.convertScaleAbs(sample_face_image, alpha=1.5, beta=50)
        faces_bright = detect_faces(bright_image)
        
        assert isinstance(faces_dark, list)
        assert isinstance(faces_bright, list)
    
    def test_face_detection_memory_usage(self, sample_face_image):
        """Test memory usage during face detection."""
        import psutil
        import gc
        
        process = psutil.Process()
        initial_memory = process.memory_info().rss
        
        # Run detection multiple times
        for _ in range(50):
            faces = detect_faces(sample_face_image)
            gc.collect()
        
        final_memory = process.memory_info().rss
        memory_increase = final_memory - initial_memory
        
        # Memory increase should be reasonable (less than 100MB)
        assert memory_increase < 100 * 1024 * 1024, f"Memory increased by {memory_increase / 1024 / 1024:.2f} MB"
    
    @staticmethod
    def rotate_image(image, angle):
        """Helper method to rotate an image."""
        height, width = image.shape[:2]
        center = (width // 2, height // 2)
        rotation_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
        return cv2.warpAffine(image, rotation_matrix, (width, height))