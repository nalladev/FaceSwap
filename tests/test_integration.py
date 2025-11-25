import os
import pytest
import cv2
import numpy as np
from face_swap import swap_faces, detect_faces

# Assuming face_swap is the module where the face swapping functions are defined

class TestFullWorkflowIntegration:
    """Integration tests for complete face swap workflows."""
    
    def test_batch_processing_workflow(self, test_data_dir, output_dir):
        """Test batch processing of multiple images."""
        # Simulate batch processing workflow
        input_images = [f for f in os.listdir(test_data_dir) if f.endswith('.jpg')]
        
        successful_swaps = 0
        failed_swaps = 0
        
        for img_file in input_images:
            try:
                img_path = os.path.join(test_data_dir, img_file)
                result = self.process_single_image(img_path, output_dir)
                if result:
                    successful_swaps += 1
                else:
                    failed_swaps += 1
            except Exception:
                failed_swaps += 1
        
        # Should have reasonable success rate
        total_images = len(input_images)
        if total_images > 0:
            success_rate = successful_swaps / total_images
            assert success_rate >= 0.5, f"Success rate {success_rate} too low"
    
    def test_error_recovery_workflow(self, test_data_dir):
        """Test system recovery from various error conditions."""
        # Test with corrupted image
        corrupted_path = os.path.join(test_data_dir, "corrupted.jpg")
        if os.path.exists(corrupted_path):
            with pytest.raises((cv2.error, ValueError, IOError)):
                swap_faces(corrupted_path, corrupted_path)
        
        # Test with non-existent file
        with pytest.raises((FileNotFoundError, IOError)):
            swap_faces("non_existent.jpg", "also_non_existent.jpg")
    
    def test_performance_benchmarks(self, sample_face_image):
        """Test performance benchmarks for face swapping operations."""
        import time
        
        # Single image processing time
        start_time = time.time()
        for _ in range(5):
            result = detect_faces(sample_face_image)
        detection_time = (time.time() - start_time) / 5
        
        # Detection should complete within reasonable time
        assert detection_time < 5.0, f"Face detection too slow: {detection_time:.2f}s"
        
        # Memory usage should be stable
        self.verify_memory_stability(sample_face_image)
    
    def process_single_image(self, image_path, output_dir):
        """Helper method to process a single image."""
        try:
            # Load image
            img = cv2.imread(image_path)
            if img is None:
                return False
            
            # Detect faces
            faces = detect_faces(img)
            
            # If faces detected, save result
            if len(faces) > 0:
                output_path = os.path.join(output_dir, f"processed_{os.path.basename(image_path)}")
                cv2.imwrite(output_path, img)
                return True
            
            return False
        except Exception:
            return False
    
    def verify_memory_stability(self, image):
        """Verify memory usage remains stable during repeated operations."""
        import psutil
        import gc
        
        process = psutil.Process()
        memory_readings = []
        
        for i in range(10):
            detect_faces(image)
            gc.collect()
            memory_readings.append(process.memory_info().rss)
        
        # Memory should not consistently increase
        memory_trend = np.polyfit(range(len(memory_readings)), memory_readings, 1)[0]
        assert memory_trend < 1024 * 1024, "Memory leak detected"  # Less than 1MB growth per iteration