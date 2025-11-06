import cv2
import numpy as np
import dlib
from typing import Tuple, Optional
import logging

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FaceSwapper:
    """
    Face swapping engine using 2D affine transformation and Poisson blending.
    Handles the core face warping and blending operations.
    """
    
    def __init__(self):
        """Initialize the face swapper."""
        self.blend_method = cv2.NORMAL_CLONE
        
    def get_convex_hull_mask(self, landmarks: np.ndarray, frame_shape: Tuple[int, int]) -> np.ndarray:
        """
        Create a convex hull mask from facial landmarks.
        
        Args:
            landmarks: Array of 68 facial landmarks
            frame_shape: Shape of the frame (height, width)
            
        Returns:
            Binary mask of the face region
        """
        # Use jawline, eyebrows, and forehead points for better coverage
        # Points for face boundary (jawline + forehead)
        face_boundary_points = np.concatenate([
            landmarks[0:17],  # Jawline
            landmarks[17:22], # Right eyebrow
            landmarks[22:27], # Left eyebrow
        ])
        
        # Create convex hull
        hull = cv2.convexHull(face_boundary_points)
        
        # Create mask
        mask = np.zeros(frame_shape[:2], dtype=np.uint8)
        cv2.fillPoly(mask, [hull], 255)
        
        return mask
    
    def get_delaunay_triangulation(self, landmarks: np.ndarray, frame_shape: Tuple[int, int]) -> list:
        """
        Compute Delaunay triangulation for landmarks.
        
        Args:
            landmarks: Array of facial landmarks
            frame_shape: Shape of the frame (height, width)
            
        Returns:
            List of triangle indices
        """
        h, w = frame_shape[:2]
        
        # Add corner points to landmarks for better triangulation
        corner_points = np.array([
            [0, 0], [w-1, 0], [w-1, h-1], [0, h-1]
        ])
        
        # Combine landmarks with corner points
        all_points = np.vstack([landmarks, corner_points])
        
        # Create rectangle for Delaunay triangulation
        rect = (0, 0, w, h)
        subdiv = cv2.Subdiv2D(rect)
        
        # Insert points
        for point in all_points:
            subdiv.insert((int(point[0]), int(point[1])))
        
        # Get triangles
        triangle_list = subdiv.getTriangleList()
        triangles = []
        
        for t in triangle_list:
            # Convert triangle coordinates to point indices
            pt1 = (int(t[0]), int(t[1]))
            pt2 = (int(t[2]), int(t[3]))
            pt3 = (int(t[4]), int(t[5]))
            
            # Find indices of these points
            indices = []
            for pt in [pt1, pt2, pt3]:
                for i, point in enumerate(all_points):
                    if abs(point[0] - pt[0]) < 1 and abs(point[1] - pt[1]) < 1:
                        indices.append(i)
                        break
            
            if len(indices) == 3:
                triangles.append(indices)
        
        return triangles
    
    def warp_triangle(self, src_img: np.ndarray, dst_img: np.ndarray,
                     src_tri: np.ndarray, dst_tri: np.ndarray) -> np.ndarray:
        """
        Warp a triangle from source to destination.
        
        Args:
            src_img: Source image
            dst_img: Destination image
            src_tri: Source triangle coordinates
            dst_tri: Destination triangle coordinates
            
        Returns:
            Warped destination image
        """
        # Get bounding rectangles
        src_rect = cv2.boundingRect(src_tri)
        dst_rect = cv2.boundingRect(dst_tri)
        
        # Offset triangles by top-left corner of bounding rectangle
        src_tri_offset = src_tri - [src_rect[0], src_rect[1]]
        dst_tri_offset = dst_tri - [dst_rect[0], dst_rect[1]]
        
        # Crop source image to bounding rectangle
        src_cropped = src_img[src_rect[1]:src_rect[1] + src_rect[3],
                             src_rect[0]:src_rect[0] + src_rect[2]]
        
        if src_cropped.size == 0:
            return dst_img
        
        # Calculate affine transformation matrix
        transform_matrix = cv2.getAffineTransform(
            src_tri_offset.astype(np.float32),
            dst_tri_offset.astype(np.float32)
        )
        
        # Warp the cropped source image
        warped = cv2.warpAffine(src_cropped, transform_matrix,
                               (dst_rect[2], dst_rect[3]),
                               flags=cv2.INTER_LINEAR,
                               borderMode=cv2.BORDER_REFLECT_101)
        
        # Create mask for the triangle
        mask = np.zeros((dst_rect[3], dst_rect[2]), dtype=np.uint8)
        cv2.fillPoly(mask, [dst_tri_offset.astype(np.int32)], 255)
        
        # Apply mask to warped image
        warped_masked = cv2.bitwise_and(warped, warped, mask=mask)
        
        # Create inverse mask
        mask_inv = cv2.bitwise_not(mask)
        dst_area = dst_img[dst_rect[1]:dst_rect[1] + dst_rect[3],
                          dst_rect[0]:dst_rect[0] + dst_rect[2]]
        dst_area_masked = cv2.bitwise_and(dst_area, dst_area, mask=mask_inv)
        
        # Combine warped triangle with destination
        final_area = cv2.add(dst_area_masked, warped_masked)
        dst_img[dst_rect[1]:dst_rect[1] + dst_rect[3],
               dst_rect[0]:dst_rect[0] + dst_rect[2]] = final_area
        
        return dst_img
    
    def align_face_simple(self, src_image: np.ndarray, src_landmarks: np.ndarray,
                         dst_landmarks: np.ndarray, frame_shape: Tuple[int, int]) -> np.ndarray:
        """
        Simple face alignment using affine transformation on key points.
        
        Args:
            src_image: Source face image
            src_landmarks: Source face landmarks
            dst_landmarks: Target face landmarks
            frame_shape: Target frame shape
            
        Returns:
            Aligned face image
        """
        # Use key facial points for alignment (eyes and mouth)
        # Left eye center, right eye center, mouth center
        src_points = np.array([
            np.mean(src_landmarks[36:42], axis=0),  # Left eye
            np.mean(src_landmarks[42:48], axis=0),  # Right eye
            np.mean(src_landmarks[48:68], axis=0),  # Mouth
        ], dtype=np.float32)
        
        dst_points = np.array([
            np.mean(dst_landmarks[36:42], axis=0),  # Left eye
            np.mean(dst_landmarks[42:48], axis=0),  # Right eye
            np.mean(dst_landmarks[48:68], axis=0),  # Mouth
        ], dtype=np.float32)
        
        # Calculate transformation matrix
        transform_matrix = cv2.getAffineTransform(src_points, dst_points)
        
        # Warp source image
        aligned_face = cv2.warpAffine(src_image, transform_matrix,
                                    (frame_shape[1], frame_shape[0]),
                                    flags=cv2.INTER_LINEAR)
        
        return aligned_face
    
    def color_correct_face(self, src_face: np.ndarray, dst_face: np.ndarray,
                          landmarks: np.ndarray) -> np.ndarray:
        """
        Apply color correction to match the target face's lighting.
        
        Args:
            src_face: Source face region
            dst_face: Target face region
            landmarks: Facial landmarks for mask creation
            
        Returns:
            Color-corrected source face
        """
        # Create mask for face region
        mask = self.get_convex_hull_mask(landmarks, src_face.shape)
        
        # Calculate mean colors in face region
        src_mean = cv2.mean(src_face, mask=mask)[:3]
        dst_mean = cv2.mean(dst_face, mask=mask)[:3]
        
        # Calculate color correction factors
        correction_factors = []
        for i in range(3):
            if src_mean[i] > 0:
                correction_factors.append(dst_mean[i] / src_mean[i])
            else:
                correction_factors.append(1.0)
        
        # Apply color correction
        corrected_face = src_face.copy().astype(np.float32)
        for i in range(3):
            corrected_face[:, :, i] *= correction_factors[i]
        
        # Clamp values to valid range
        corrected_face = np.clip(corrected_face, 0, 255).astype(np.uint8)
        
        return corrected_face
    
    def create_seamless_mask(self, landmarks: np.ndarray, frame_shape: Tuple[int, int],
                           feather_amount: int = 10) -> np.ndarray:
        """
        Create a feathered mask for seamless blending.
        
        Args:
            landmarks: Facial landmarks
            frame_shape: Shape of the frame
            feather_amount: Amount of feathering in pixels
            
        Returns:
            Feathered mask
        """
        # Create base mask
        mask = self.get_convex_hull_mask(landmarks, frame_shape)
        
        # Apply Gaussian blur for feathering
        if feather_amount > 0:
            mask = cv2.GaussianBlur(mask, (feather_amount * 2 + 1, feather_amount * 2 + 1), 0)
        
        return mask
    
    def swap_face(self, target_frame: np.ndarray, target_landmarks: np.ndarray,
                  source_image: np.ndarray, source_landmarks: np.ndarray) -> np.ndarray:
        """
        Perform face swap using 2D warping and blending.
        
        Args:
            target_frame: Target video frame
            target_landmarks: Target face landmarks
            source_image: Source face image
            source_landmarks: Source face landmarks
            
        Returns:
            Frame with face swapped
        """
        try:
            # Create a copy of the target frame
            result_frame = target_frame.copy()
            
            # Step 1: Align source face to target landmarks
            aligned_source = self.align_face_simple(
                source_image, source_landmarks, target_landmarks, target_frame.shape
            )
            
            # Step 2: Create mask for blending
            mask = self.create_seamless_mask(target_landmarks, target_frame.shape, feather_amount=6)
            
            # Step 3: Get center point for seamless cloning
            center = np.mean(target_landmarks, axis=0).astype(int)
            center = tuple(center)
            
            # Step 4: Apply color correction
            target_face_region = self.extract_face_region(target_frame, target_landmarks)
            source_face_region = self.extract_face_region(aligned_source, target_landmarks)
            
            if target_face_region is not None and source_face_region is not None:
                aligned_source_corrected = self.color_correct_face(
                    aligned_source, target_frame, target_landmarks
                )
            else:
                aligned_source_corrected = aligned_source
            
            # Step 5: Seamless cloning (Poisson blending)
            try:
                result_frame = cv2.seamlessClone(
                    aligned_source_corrected,
                    result_frame,
                    mask,
                    center,
                    self.blend_method
                )
            except cv2.error as e:
                logger.warning(f"Seamless cloning failed, using simple blending: {e}")
                # Fallback to simple alpha blending
                mask_norm = mask.astype(np.float32) / 255.0
                mask_norm = np.stack([mask_norm] * 3, axis=2)
                
                result_frame = (aligned_source_corrected * mask_norm + 
                              target_frame * (1 - mask_norm)).astype(np.uint8)
            
            return result_frame
            
        except Exception as e:
            logger.error(f"Face swap failed: {e}")
            return target_frame
    
    def extract_face_region(self, frame: np.ndarray, landmarks: np.ndarray) -> Optional[np.ndarray]:
        """
        Extract face region based on landmarks.
        
        Args:
            frame: Input frame
            landmarks: Facial landmarks
            
        Returns:
            Extracted face region or None if extraction fails
        """
        try:
            # Get bounding box with padding
            x_coords = landmarks[:, 0]
            y_coords = landmarks[:, 1]
            
            x_min = max(0, int(np.min(x_coords)) - 20)
            y_min = max(0, int(np.min(y_coords)) - 20)
            x_max = min(frame.shape[1], int(np.max(x_coords)) + 20)
            y_max = min(frame.shape[0], int(np.max(y_coords)) + 20)
            
            if x_max > x_min and y_max > y_min:
                return frame[y_min:y_max, x_min:x_max]
            else:
                return None
                
        except Exception as e:
            logger.warning(f"Face region extraction failed: {e}")
            return None
    
    def process_video_frame(self, frame: np.ndarray, face_detector, face_data: dict) -> np.ndarray:
        """
        Process a single video frame for face swapping.
        
        Args:
            frame: Input video frame
            face_detector: FaceDetector instance
            face_data: Dictionary containing unique faces and their swap data
            
        Returns:
            Processed frame with face swaps applied
        """
        try:
            # Convert BGR to RGB for face detection
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Detect faces in the frame
            faces = face_detector.detect_faces(rgb_frame, scale_factor=0.5)
            
            # Process each detected face
            for face_rect in faces:
                try:
                    # Get landmarks and encoding for this face
                    landmarks = face_detector.get_face_landmarks(rgb_frame, face_rect)
                    dlib_landmarks = face_detector.predictor(rgb_frame, face_rect)
                    face_encoding = face_detector.get_face_encoding(rgb_frame, dlib_landmarks)
                    
                    # Find matching unique face
                    matched_face = face_detector.get_face_match(face_encoding)
                    
                    if matched_face and matched_face['swap_image'] is not None:
                        # Perform face swap
                        frame = self.swap_face(
                            frame,
                            landmarks,
                            matched_face['swap_image'],
                            matched_face['swap_landmarks']
                        )
                        
                except Exception as e:
                    logger.warning(f"Error processing face in frame: {e}")
                    continue
            
            return frame
            
        except Exception as e:
            logger.error(f"Frame processing failed: {e}")
            return frame
    
    def set_blend_method(self, method: int):
        """
        Set the blending method for seamless cloning.
        
        Args:
            method: OpenCV blending method (e.g., cv2.NORMAL_CLONE, cv2.MIXED_CLONE)
        """
        self.blend_method = method
        logger.info(f"Blend method set to: {method}")