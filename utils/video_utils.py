import cv2
import numpy as np
import os
from typing import Tuple, Optional, List
import logging

logger = logging.getLogger(__name__)

class VideoUtils:
    """
    Utility class for video processing operations.
    Provides helper functions for video file handling and analysis.
    """
    
    @staticmethod
    def get_video_info(video_path: str) -> dict:
        """Get comprehensive information about a video file."""
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Could not open video: {video_path}")
            
            info = {
                'path': video_path,
                'filename': os.path.basename(video_path),
                'width': int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'height': int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'fps': cap.get(cv2.CAP_PROP_FPS),
                'frame_count': int(cap.get(cv2.CAP_PROP_FRAME_COUNT)),
                'duration': 0,
                'size_mb': 0
            }
            
            # Calculate duration
            if info['fps'] > 0:
                info['duration'] = info['frame_count'] / info['fps']
            
            # Get file size
            if os.path.exists(video_path):
                info['size_mb'] = os.path.getsize(video_path) / (1024 * 1024)
            
            cap.release()
            return info
            
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return {}
    
    @staticmethod
    def is_valid_video(video_path: str) -> bool:
        """Check if a file is a valid video that can be opened."""
        if not os.path.exists(video_path):
            return False
        
        try:
            cap = cv2.VideoCapture(video_path)
            is_valid = cap.isOpened()
            
            if is_valid:
                # Try to read first frame
                ret, frame = cap.read()
                is_valid = ret and frame is not None
            
            cap.release()
            return is_valid
            
        except Exception:
            return False
    
    @staticmethod
    def extract_frames(video_path: str, output_dir: str, 
                      frame_interval: int = 1, max_frames: int = None) -> List[str]:
        """Extract frames from video as image files."""
        try:
            os.makedirs(output_dir, exist_ok=True)
            
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                raise ValueError(f"Could not open video: {video_path}")
            
            frame_paths = []
            frame_count = 0
            extracted_count = 0
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Check if we should extract this frame
                if frame_count % frame_interval == 0:
                    if max_frames and extracted_count >= max_frames:
                        break
                    
                    # Save frame
                    frame_filename = f"frame_{extracted_count:06d}.jpg"
                    frame_path = os.path.join(output_dir, frame_filename)
                    
                    success = cv2.imwrite(frame_path, frame)
                    if success:
                        frame_paths.append(frame_path)
                        extracted_count += 1
                
                frame_count += 1
            
            cap.release()
            logger.info(f"Extracted {len(frame_paths)} frames to {output_dir}")
            return frame_paths
            
        except Exception as e:
            logger.error(f"Error extracting frames: {e}")
            return []
    
    @staticmethod
    def get_frame_at_time(video_path: str, time_seconds: float) -> Optional[np.ndarray]:
        """Extract a single frame at a specific time."""
        try:
            cap = cv2.VideoCapture(video_path)
            if not cap.isOpened():
                return None
            
            fps = cap.get(cv2.CAP_PROP_FPS)
            frame_number = int(time_seconds * fps)
            
            # Seek to frame
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)
            
            ret, frame = cap.read()
            cap.release()
            
            return frame if ret else None
            
        except Exception as e:
            logger.error(f"Error extracting frame at time {time_seconds}: {e}")
            return None