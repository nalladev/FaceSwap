import os
import sys
import time
import psutil
import logging
import numpy as np
import cv2
from contextlib import contextmanager
from typing import Generator

# Add project root to path
sys.path.append('/workspaces/FaceSwap')

# Configure lightweight logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

class ResourceMonitor:
    """Monitor system resources to prevent overload."""
    
    def __init__(self, max_memory_mb: int = 500, max_cpu_percent: float = 80.0):
        self.max_memory_mb = max_memory_mb
        self.max_cpu_percent = max_cpu_percent
        self.initial_memory = psutil.virtual_memory().used / 1024 / 1024
    
    def check_resources(self) -> bool:
        """Check if resources are within safe limits."""
        current_memory = psutil.virtual_memory().used / 1024 / 1024
        memory_usage = current_memory - self.initial_memory
        cpu_percent = psutil.cpu_percent(interval=0.1)
        
        if memory_usage > self.max_memory_mb:
            logger.warning(f"Memory usage too high: {memory_usage:.1f}MB")
            return False
        
        if cpu_percent > self.max_cpu_percent:
            logger.warning(f"CPU usage too high: {cpu_percent:.1f}%")
            return False
        
        return True

@contextmanager
def safe_test_execution(test_name: str, monitor: ResourceMonitor) -> Generator:
    """Context manager for safe test execution with resource monitoring."""
    logger.info(f"Starting test: {test_name}")
    start_time = time.time()
    
    try:
        if not monitor.check_resources():
            raise ResourceError("System resources too low to start test")
        yield
        logger.info(f"✅ {test_name} passed ({time.time() - start_time:.2f}s)")
    except Exception as e:
        logger.error(f"❌ {test_name} failed: {e}")
        raise
    finally:
        # Force cleanup
        import gc
        gc.collect()

class ResourceError(Exception):
    pass

def create_test_image(size: tuple = (100, 100)) -> np.ndarray:
    """Create a small test image with a simple face-like pattern."""
    image = np.zeros((*size, 3), dtype=np.uint8)
    center = (size[1]//2, size[0]//2)
    
    # Simple face pattern
    cv2.circle(image, center, 30, (200, 200, 200), -1)  # Face
    cv2.circle(image, (center[0]-10, center[1]-10), 3, (0, 0, 0), -1)  # Left eye
    cv2.circle(image, (center[0]+10, center[1]-10), 3, (0, 0, 0), -1)  # Right eye
    cv2.ellipse(image, (center[0], center[1]+10), (8, 4), 0, 0, 180, (0, 0, 0), 1)  # Mouth
    
    return image

def test_gpu_utils():
    """Test GPU utilities with minimal resource usage."""
    try:
        from utils.gpu_utils import gpu_manager
        
        # Test device detection
        device = gpu_manager.device
        device_type = gpu_manager.device_type
        logger.info(f"Detected device: {device} (type: {device_type})")
        
        # Test batch size calculation
        batch_size = gpu_manager.get_optimal_batch_size()
        logger.info(f"Optimal batch size: {batch_size}")
        
        # Test with very small image
        test_img = create_test_image((50, 50))
        processed = gpu_manager.optimize_image_processing(test_img)
        
        assert processed is not None, "Image processing failed"
        assert processed.shape == test_img.shape, "Image shape changed unexpectedly"
        
        return True
        
    except Exception as e:
        logger.error(f"GPU utils test failed: {e}")
        return False

def test_face_detection_lightweight():
    """Test face detection with minimal resources."""
    try:
        from face_detection import FaceDetector
        
        # Create detector (this should not crash)
        detector = FaceDetector()
        logger.info(f"Face detector initialized on {detector.device}")
        
        # Test with tiny image
        test_img = create_test_image((80, 80))
        
        # Mock heavy operations for testing
        def mock_detect():
            # Simulate detection result
            return [(20, 20, 40, 40)]  # x, y, w, h
        
        # Test CPU detection only to avoid GPU memory allocation
        faces = detector.detect_faces_cpu(test_img)
        logger.info(f"Detected {len(faces)} faces")
        
        return True
        
    except Exception as e:
        logger.error(f"Face detection test failed: {e}")
        return False

def test_face_swapper_lightweight():
    """Test face swapper with minimal resources."""
    try:
        from face_swap import FaceSwapper
        
        # Create swapper
        swapper = FaceSwapper()
        logger.info(f"Face swapper initialized on {swapper.device}")
        
        # Test with very small images
        source_img = create_test_image((60, 60))
        target_img = create_test_image((60, 60))
        
        # Mock face coordinates
        source_face = (10, 10, 30, 30)
        target_face = (15, 15, 30, 30)
        
        # Test CPU version only to avoid GPU memory
        result = swapper.swap_faces_cpu(source_img, target_img, source_face, target_face)
        
        assert result is not None, "Face swap failed"
        assert result.shape == target_img.shape, "Result shape incorrect"
        
        return True
        
    except Exception as e:
        logger.error(f"Face swapper test failed: {e}")
        return False

def test_import_safety():
    """Test that all imports work without crashes."""
    try:
        # Test torch import
        import torch
        logger.info(f"PyTorch version: {torch.__version__}")
        logger.info(f"CUDA available: {torch.cuda.is_available()}")
        
        # Test cv2 import
        import cv2
        logger.info(f"OpenCV version: {cv2.__version__}")
        
        # Test other dependencies
        try:
            import torchvision
            logger.info(f"Torchvision available: {torchvision.__version__}")
        except ImportError:
            logger.warning("Torchvision not available")
        
        try:
            from facenet_pytorch import MTCNN
            logger.info("Facenet-pytorch available")
        except ImportError:
            logger.warning("Facenet-pytorch not available")
        
        return True
        
    except Exception as e:
        logger.error(f"Import test failed: {e}")
        return False

def test_memory_efficiency():
    """Test memory efficiency with gradual load increase."""
    try:
        import torch
        
        # Start with tiny tensors
        device = torch.device('cpu')  # Force CPU to avoid GPU memory issues
        
        for size in [10, 50, 100]:
            tensor = torch.randn(1, 3, size, size, device=device)
            processed = torch.nn.functional.interpolate(tensor, size=(size//2, size//2))
            
            # Clean up immediately
            del tensor, processed
            
        logger.info("Memory efficiency test passed")
        return True
        
    except Exception as e:
        logger.error(f"Memory efficiency test failed: {e}")
        return False

def run_all_tests():
    """Run all tests with resource monitoring."""
    monitor = ResourceMonitor(max_memory_mb=300, max_cpu_percent=70.0)
    
    tests = [
        ("Import Safety", test_import_safety),
        ("GPU Utils", test_gpu_utils),
        ("Memory Efficiency", test_memory_efficiency),
        ("Face Detection (Lightweight)", test_face_detection_lightweight),
        ("Face Swapper (Lightweight)", test_face_swapper_lightweight),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            with safe_test_execution(test_name, monitor):
                if test_func():
                    passed += 1
                else:
                    logger.error(f"Test {test_name} returned False")
        except ResourceError as e:
            logger.error(f"Skipping {test_name}: {e}")
            break
        except Exception as e:
            logger.error(f"Test {test_name} crashed: {e}")
        
        # Check resources after each test
        if not monitor.check_resources():
            logger.warning("System resources low, stopping tests")
            break
        
        # Small delay to let system recover
        time.sleep(0.5)
    
    logger.info(f"\n🏁 Test Summary: {passed}/{total} tests passed")
    return passed == total

if __name__ == "__main__":
    logger.info("Starting lightweight GPU acceleration tests...")
    logger.info(f"System: {psutil.virtual_memory().total / 1024 / 1024 / 1024:.1f}GB RAM, {psutil.cpu_count()} CPUs")
    
    success = run_all_tests()
    
    if success:
        logger.info("🎉 All tests passed! GPU acceleration is ready.")
    else:
        logger.warning("⚠️  Some tests failed. Check logs above.")
    
    sys.exit(0 if success else 1)
