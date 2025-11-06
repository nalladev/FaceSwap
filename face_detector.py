import cv2
import dlib
import numpy as np
import os
from typing import List, Tuple, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FaceDetector:
    """
    Core face detection and recognition system using Dlib.
    Handles face detection, landmark prediction, and face encoding.
    """
    
    def __init__(self, models_dir: str = "models"):
        """
        Initialize the face detector with Dlib models.
        
        Args:
            models_dir: Directory containing the Dlib model files
        """
        self.models_dir = models_dir
        self.detector = None
        self.predictor = None
        self.face_encoder = None
        self.unique_faces = []
        self.face_recognition_threshold = 0.6
        
        self._load_models()
    
    def _load_models(self):
        """Load Dlib models for face detection and recognition."""
        try:
            # Load face detector
            self.detector = dlib.get_frontal_face_detector()
            logger.info("Face detector loaded successfully")
            
            # Load facial landmark predictor
            predictor_path = os.path.join(self.models_dir, "shape_predictor_68_face_landmarks.dat")
            if not os.path.exists(predictor_path):
                raise FileNotFoundError(f"Facial landmark model not found at {predictor_path}")
            
            self.predictor = dlib.shape_predictor(predictor_path)
            logger.info("Facial landmark predictor loaded successfully")
            
            # Load face recognition model
            encoder_path = os.path.join(self.models_dir, "dlib_face_recognition_resnet_model_v1.dat")
            if not os.path.exists(encoder_path):
                raise FileNotFoundError(f"Face recognition model not found at {encoder_path}")
            
            self.face_encoder = dlib.face_recognition_model_v1(encoder_path)
            logger.info("Face recognition model loaded successfully")
            
        except Exception as e:
            logger.error(f"Error loading models: {e}")
            raise
    
    def detect_faces(self, frame: np.ndarray, scale_factor: float = 0.5) -> List[dlib.rectangle]:
        """
        Detect faces in a frame.
        
        Args:
            frame: Input image frame
            scale_factor: Scale factor for faster detection (smaller = faster)
            
        Returns:
            List of face rectangles
        """
        # Scale down for faster detection if needed
        if scale_factor < 1.0:
            small_frame = cv2.resize(frame, None, fx=scale_factor, fy=scale_factor)
            faces = self.detector(small_frame)
            # Scale back up the coordinates
            scaled_faces = []
            for face in faces:
                scaled_face = dlib.rectangle(
                    int(face.left() / scale_factor),
                    int(face.top() / scale_factor),
                    int(face.right() / scale_factor),
                    int(face.bottom() / scale_factor)
                )
                scaled_faces.append(scaled_face)
            return scaled_faces
        else:
            return self.detector(frame)
    
    def get_face_landmarks(self, frame: np.ndarray, face_rect: dlib.rectangle) -> np.ndarray:
        """
        Get 68 facial landmarks for a detected face.
        
        Args:
            frame: Input image frame
            face_rect: Face rectangle from detection
            
        Returns:
            Array of 68 (x, y) landmark coordinates
        """
        landmarks = self.predictor(frame, face_rect)
        landmarks_array = np.array([[p.x, p.y] for p in landmarks.parts()])
        return landmarks_array
    
    def get_face_encoding(self, frame: np.ndarray, landmarks) -> np.ndarray:
        """
        Get 128-dimensional face encoding.
        
        Args:
            frame: Input image frame
            landmarks: Facial landmarks from predictor
            
        Returns:
            128-dimensional face encoding vector
        """
        face_encoding = self.face_encoder.compute_face_descriptor(frame, landmarks)
        return np.array(face_encoding)
    
    def crop_face(self, frame: np.ndarray, face_rect: dlib.rectangle, padding: int = 50) -> np.ndarray:
        """
        Crop face from frame with padding.
        
        Args:
            frame: Input image frame
            face_rect: Face rectangle
            padding: Padding around face in pixels
            
        Returns:
            Cropped face image
        """
        h, w = frame.shape[:2]
        
        # Calculate crop coordinates with padding
        left = max(0, face_rect.left() - padding)
        top = max(0, face_rect.top() - padding)
        right = min(w, face_rect.right() + padding)
        bottom = min(h, face_rect.bottom() + padding)
        
        return frame[top:bottom, left:right]
    
    def find_similar_face(self, face_encoding: np.ndarray) -> Optional[int]:
        """
        Find if a face encoding matches any existing unique face.
        
        Args:
            face_encoding: 128-dimensional face encoding
            
        Returns:
            Index of matching face in unique_faces list, or None if no match
        """
        for i, unique_face in enumerate(self.unique_faces):
            # Calculate Euclidean distance between encodings
            distance = np.linalg.norm(face_encoding - unique_face['encoding'])
            
            if distance < self.face_recognition_threshold:
                return i
        
        return None
    
    def add_unique_face(self, face_image: np.ndarray, face_encoding: np.ndarray, 
                       face_rect: dlib.rectangle, landmarks: np.ndarray) -> int:
        """
        Add a new unique face to the collection.
        
        Args:
            face_image: Cropped face image
            face_encoding: 128-dimensional face encoding
            face_rect: Original face rectangle
            landmarks: Facial landmarks
            
        Returns:
            Index of the newly added face
        """
        unique_face = {
            'image': face_image,
            'encoding': face_encoding,
            'rect': face_rect,
            'landmarks': landmarks,
            'swap_image_path': None,
            'swap_image': None,
            'swap_landmarks': None
        }
        
        self.unique_faces.append(unique_face)
        return len(self.unique_faces) - 1
    
    def set_swap_image(self, face_index: int, swap_image_path: str):
        """
        Set swap image for a unique face.
        
        Args:
            face_index: Index of face in unique_faces list
            swap_image_path: Path to swap image file
        """
        if 0 <= face_index < len(self.unique_faces):
            # Load and process the swap image
            swap_image = cv2.imread(swap_image_path)
            if swap_image is None:
                raise ValueError(f"Could not load swap image: {swap_image_path}")
            
            # Detect face in swap image
            faces = self.detect_faces(swap_image)
            if not faces:
                raise ValueError(f"No face detected in swap image: {swap_image_path}")
            
            # Use the first detected face
            face_rect = faces[0]
            landmarks = self.get_face_landmarks(swap_image, face_rect)
            
            # Store swap image data
            self.unique_faces[face_index]['swap_image_path'] = swap_image_path
            self.unique_faces[face_index]['swap_image'] = swap_image
            self.unique_faces[face_index]['swap_landmarks'] = landmarks
            
            logger.info(f"Swap image set for face {face_index}: {swap_image_path}")
        else:
            raise IndexError(f"Face index {face_index} out of range")
    
    def scan_video_for_faces(self, video_path: str, progress_callback=None) -> List[dict]:
        """
        Scan entire video to find all unique faces.
        
        Args:
            video_path: Path to video file
            progress_callback: Optional callback function for progress updates
            
        Returns:
            List of unique face dictionaries
        """
        # Clear existing faces
        self.unique_faces = []
        
        # Open video
        cap = cv2.VideoCapture(video_path)
        if not cap.isOpened():
            raise ValueError(f"Could not open video: {video_path}")
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        frame_count = 0
        
        # Skip frames for faster processing (analyze every 10th frame)
        frame_skip = 10
        
        logger.info(f"Scanning video for faces: {video_path}")
        logger.info(f"Total frames: {total_frames}, analyzing every {frame_skip}th frame")
        
        try:
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                frame_count += 1
                
                # Skip frames for faster processing
                if frame_count % frame_skip != 0:
                    continue
                
                # Convert BGR to RGB for Dlib
                rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                
                # Detect faces in frame
                faces = self.detect_faces(rgb_frame, scale_factor=0.5)
                
                for face_rect in faces:
                    try:
                        # Get landmarks and encoding
                        landmarks = self.get_face_landmarks(rgb_frame, face_rect)
                        dlib_landmarks = self.predictor(rgb_frame, face_rect)
                        face_encoding = self.get_face_encoding(rgb_frame, dlib_landmarks)
                        
                        # Check if this is a new unique face
                        similar_face_index = self.find_similar_face(face_encoding)
                        
                        if similar_face_index is None:
                            # New unique face found
                            face_image = self.crop_face(rgb_frame, face_rect)
                            face_index = self.add_unique_face(face_image, face_encoding, face_rect, landmarks)
                            logger.info(f"New unique face found: #{face_index}")
                    
                    except Exception as e:
                        logger.warning(f"Error processing face in frame {frame_count}: {e}")
                        continue
                
                # Update progress
                if progress_callback:
                    progress = (frame_count / total_frames) * 100
                    progress_callback(progress)
        
        finally:
            cap.release()
        
        logger.info(f"Face scanning complete. Found {len(self.unique_faces)} unique faces.")
        return self.unique_faces
    
    def get_unique_faces(self) -> List[dict]:
        """Get the list of unique faces found."""
        return self.unique_faces
    
    def clear_unique_faces(self):
        """Clear all unique faces."""
        self.unique_faces = []
        logger.info("Unique faces cleared")
    
    def is_ready_for_processing(self) -> bool:
        """Check if all unique faces have swap images assigned."""
        if not self.unique_faces:
            return False
        
        for face in self.unique_faces:
            if face['swap_image_path'] is None:
                return False
        
        return True
    
    def get_face_match(self, face_encoding: np.ndarray) -> Optional[dict]:
        """
        Find the best matching unique face for a given encoding.
        
        Args:
            face_encoding: 128-dimensional face encoding to match
            
        Returns:
            Dictionary of matching unique face, or None if no match
        """
        best_match_index = self.find_similar_face(face_encoding)
        
        if best_match_index is not None:
            return self.unique_faces[best_match_index]
        
        return None