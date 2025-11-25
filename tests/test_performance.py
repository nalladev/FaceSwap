import pytest
import time
import psutil
import gc
import numpy as np
from memory_profiler import profile

class TestPerformanceBenchmarks:
    """Performance and stress tests for the face swap application."""
    
    @pytest.mark.performance
    def test_face_detection_speed(self, sample_face_image):
        """Benchmark face detection speed."""
        iterations = 100
        times = []
        
        for _ in range(iterations):
            start_time = time.perf_counter()
            detect_faces(sample_face_image)
            end_time = time.perf_counter()
            times.append(end_time - start_time)
        
        avg_time = np.mean(times)
        std_time = np.std(times)
        
        # Performance assertions
        assert avg_time < 1.0, f"Average detection time {avg_time:.3f}s too slow"
        assert std_time < 0.5, f"Detection time variance {std_time:.3f}s too high"
    
    @pytest.mark.performance
    @pytest.mark.slow
    def test_stress_large_batch(self, test_data_dir):
        """Stress test with large batch of images."""
        # Simulate processing many images
        image_paths = []
        for root, dirs, files in os.walk(test_data_dir):
            for file in files:
                if file.lower().endswith(('.jpg', '.png', '.jpeg')):
                    image_paths.append(os.path.join(root, file))
        
        # Process each image multiple times to simulate load
        start_memory = psutil.Process().memory_info().rss
        
        for _ in range(5):  # Process each image 5 times
            for img_path in image_paths:
                try:
                    img = cv2.imread(img_path)
                    if img is not None:
                        detect_faces(img)
                except Exception:
                    pass  # Continue with other images
        
        end_memory = psutil.Process().memory_info().rss
        memory_increase = end_memory - start_memory
        
        # Memory increase should be reasonable
        assert memory_increase < 500 * 1024 * 1024, f"Memory increased by {memory_increase / 1024 / 1024:.2f} MB"
    
    def test_concurrent_processing_performance(self, sample_face_image):
        """Test performance under concurrent load."""
        import concurrent.futures
        import threading
        
        def process_image(image, thread_id):
            start_time = time.perf_counter()
            faces = detect_faces(image)
            end_time = time.perf_counter()
            return end_time - start_time, len(faces)
        
        # Run concurrent processing
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = [executor.submit(process_image, sample_face_image, i) 
                      for i in range(20)]
            results = [future.result() for future in concurrent.futures.as_completed(futures)]
        
        times = [result[0] for result in results]
        avg_concurrent_time = np.mean(times)
        
        # Concurrent processing shouldn't be dramatically slower
        assert avg_concurrent_time < 2.0, f"Concurrent processing too slow: {avg_concurrent_time:.3f}s"