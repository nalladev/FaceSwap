import torch
import cv2
import numpy as np
import logging
from typing import Optional, Tuple

logger = logging.getLogger(__name__)

class GPUManager:
    def __init__(self):
        self.device = self._detect_device()
        self.device_type = self._get_device_type()
        self.opencv_gpu = self._check_opencv_gpu()
        
    def _detect_device(self) -> torch.device:
        """Detect the best available device for computation."""
        if torch.cuda.is_available():
            device = torch.device('cuda')
            logger.info(f"CUDA GPU detected: {torch.cuda.get_device_name()}")
        elif hasattr(torch.backends, 'mps') and torch.backends.mps.is_available():
            device = torch.device('mps')
            logger.info("Apple Metal Performance Shaders (MPS) detected")
        else:
            device = torch.device('cpu')
            logger.info("Using CPU for computation")
        return device
    
    def _get_device_type(self) -> str:
        """Get the type of device being used."""
        if self.device.type == 'cuda':
            return 'nvidia'
        elif self.device.type == 'mps':
            return 'apple'
        else:
            return 'cpu'
    
    def _check_opencv_gpu(self) -> bool:
        """Check if OpenCV was built with GPU support."""
        try:
            if cv2.cuda.getCudaEnabledDeviceCount() > 0:
                logger.info(f"OpenCV CUDA support available: {cv2.cuda.getCudaEnabledDeviceCount()} devices")
                return True
        except:
            pass
        logger.info("OpenCV GPU support not available")
        return False
    
    def get_optimal_batch_size(self) -> int:
        """Get optimal batch size based on available GPU memory."""
        if self.device.type == 'cuda':
            try:
                gpu_memory = torch.cuda.get_device_properties(0).total_memory
                # Rough estimation: use 1/4 of GPU memory for batch processing
                if gpu_memory > 8 * 1024**3:  # 8GB+
                    return 8
                elif gpu_memory > 4 * 1024**3:  # 4GB+
                    return 4
                else:
                    return 2
            except:
                return 2
        elif self.device.type == 'mps':
            return 4  # Conservative for Apple Silicon
        else:
            return 1  # CPU fallback
    
    def create_gpu_mat(self, image: np.ndarray) -> Optional[cv2.cuda.GpuMat]:
        """Create GPU matrix if OpenCV GPU support is available."""
        if self.opencv_gpu and self.device.type == 'cuda':
            try:
                gpu_mat = cv2.cuda.GpuMat()
                gpu_mat.upload(image)
                return gpu_mat
            except:
                return None
        return None
    
    def optimize_image_processing(self, image: np.ndarray) -> np.ndarray:
        """Optimize image processing using available GPU acceleration."""
        if self.opencv_gpu and self.device.type == 'cuda':
            try:
                gpu_img = self.create_gpu_mat(image)
                if gpu_img is not None:
                    # Perform GPU-accelerated operations here
                    result = cv2.cuda.GpuMat()
                    # Example: GPU-accelerated bilateral filter
                    cv2.cuda.bilateralFilter(gpu_img, result, -1, 80, 80)
                    output = result.download()
                    return output
            except Exception as e:
                logger.warning(f"GPU processing failed, falling back to CPU: {e}")
        
        # CPU fallback
        return cv2.bilateralFilter(image, -1, 80, 80)

# Global GPU manager instance
gpu_manager = GPUManager()
