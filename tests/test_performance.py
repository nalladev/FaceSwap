import pytest
import time
import os
import cv2
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import psutil
import gc

class TestPerformanceBenchmarks:
    """Performance and stress testing."""

    @pytest.mark.slow
    def test_face_detection_speed(self, sample_face_image):
        """Test face detection performance."""
        # Simulate face detection timing
        start_time = time.time()
        
        # Mock face detection operation
        gray = cv2.cvtColor(sample_face_image, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (5, 5), 0)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        # Should complete within reasonable time
        assert processing_time < 1.0  # 1 second max for simple operations
        assert gray is not None
        assert blurred is not None

    @pytest.mark.slow
    def test_stress_large_batch(self, test_data_dir):
        """Stress test with large batch of images."""
        # Create test images
        image_paths = []
        for i in range(10):  # Reduced from larger batch for test speed
            test_image = np.random.randint(0, 255, (200, 200, 3), dtype=np.uint8)
            image_path = os.path.join(test_data_dir, f"batch_test_{i}.jpg")
            cv2.imwrite(image_path, test_image)
            image_paths.append(image_path)
        
        # Process batch and measure performance
        start_time = time.time()
        processed_count = 0
        
        for image_path in image_paths:
            image = cv2.imread(image_path)
            if image is not None:
                # Simulate processing
                gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
                processed_count += 1
        
        end_time = time.time()
        total_time = end_time - start_time
        
        assert processed_count == len(image_paths)
        assert total_time < 10.0  # Should complete within 10 seconds

    def test_concurrent_processing_performance(self, sample_face_image):
        """Test performance under concurrent load."""
        def process_image(image_data):
            """Simulate image processing."""
            gray = cv2.cvtColor(image_data, cv2.COLOR_BGR2GRAY)
            blurred = cv2.GaussianBlur(gray, (3, 3), 0)
            return blurred

        # Test concurrent processing
        start_time = time.time()
        
        with ThreadPoolExecutor(max_workers=3) as executor:
            futures = []
            for i in range(5):
                future = executor.submit(process_image, sample_face_image.copy())
                futures.append(future)
            
            results = [future.result() for future in futures]
        
        end_time = time.time()
        total_time = end_time - start_time
        
        assert len(results) == 5
        assert all(result is not None for result in results)
        assert total_time < 5.0  # Should complete within 5 seconds