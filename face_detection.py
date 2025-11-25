import cv2
import numpy as np
import torch
import torchvision.transforms as transforms
from utils.gpu_utils import gpu_manager
import logging

logger = logging.getLogger(__name__)

class FaceDetector:
    def __init__(self):
        self.device = gpu_manager.device
        self.batch_size = gpu_manager.get_optimal_batch_size()
        
        # Initialize face detection models with GPU support
        self._init_detectors()
        
    def _init_detectors(self):
        """Initialize face detection models optimized for available hardware."""
        try:
            # Try to load GPU-optimized models
            if self.device.type in ['cuda', 'mps']:
                # Use GPU-accelerated MTCNN or similar
                from facenet_pytorch import MTCNN
                self.mtcnn = MTCNN(
                    device=self.device,
                    select_largest=False,
                    post_process=False
                )
                logger.info(f"Loaded MTCNN on {self.device}")
            else:
                # CPU fallback
                self._init_cpu_detector()
        except ImportError:
            logger.warning("GPU-optimized face detection not available, using CPU fallback")
            self._init_cpu_detector()
    
    def _init_cpu_detector(self):
        """Initialize CPU-based face detector."""
        # Load OpenCV Haar cascades or DNN models
        self.face_cascade = cv2.CascadeClassifier(
            cv2.data.haarcascades + 'haarcascade_frontalface_default.xml'
        )
        
        # Try to load DNN face detector if available
        try:
            self.dnn_net = cv2.dnn.readNetFromTensorflow('models/opencv_face_detector_uint8.pb',
                                                        'models/opencv_face_detector.pbtxt')
            if gpu_manager.opencv_gpu and self.device.type == 'cuda':
                self.dnn_net.setPreferableBackend(cv2.dnn.DNN_BACKEND_CUDA)
                self.dnn_net.setPreferableTarget(cv2.dnn.DNN_TARGET_CUDA)
        except:
            self.dnn_net = None
    
    def detect_faces_gpu(self, image: np.ndarray) -> list:
        """GPU-accelerated face detection."""
        if hasattr(self, 'mtcnn') and self.device.type in ['cuda', 'mps']:
            try:
                # Convert to tensor and move to GPU
                image_tensor = transforms.ToTensor()(image).unsqueeze(0).to(self.device)
                
                # Detect faces using GPU
                boxes, probs = self.mtcnn.detect(image_tensor)
                
                if boxes is not None:
                    faces = []
                    for box, prob in zip(boxes[0], probs[0]):
                        if prob > 0.9:  # Confidence threshold
                            x1, y1, x2, y2 = box.astype(int)
                            faces.append((x1, y1, x2-x1, y2-y1))
                    return faces
            except Exception as e:
                logger.warning(f"GPU face detection failed: {e}")
        
        # CPU fallback
        return self.detect_faces_cpu(image)
    
    def detect_faces_cpu(self, image: np.ndarray) -> list:
        """CPU-based face detection with optional GPU preprocessing."""
        # Use GPU for image preprocessing if available
        processed_image = gpu_manager.optimize_image_processing(image)
        gray = cv2.cvtColor(processed_image, cv2.COLOR_BGR2GRAY)
        
        # Try DNN detector first
        if self.dnn_net is not None:
            try:
                blob = cv2.dnn.blobFromImage(image, 1.0, (300, 300), [104, 117, 123])
                self.dnn_net.setInput(blob)
                detections = self.dnn_net.forward()
                
                faces = []
                h, w = image.shape[:2]
                for i in range(detections.shape[2]):
                    confidence = detections[0, 0, i, 2]
                    if confidence > 0.5:
                        x1 = int(detections[0, 0, i, 3] * w)
                        y1 = int(detections[0, 0, i, 4] * h)
                        x2 = int(detections[0, 0, i, 5] * w)
                        y2 = int(detections[0, 0, i, 6] * h)
                        faces.append((x1, y1, x2-x1, y2-y1))
                return faces
            except:
                pass
        
        # Haar cascade fallback
        faces = self.face_cascade.detectMultiScale(gray, 1.1, 4)
        return faces.tolist() if len(faces) > 0 else []

    def detect_faces(self, image: np.ndarray) -> list:
        """Main face detection method that chooses optimal approach."""
        return self.detect_faces_gpu(image)
