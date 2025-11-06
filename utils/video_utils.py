import cv2
import numpy as np
import os
from typing import Tuple, Optional, List
import logging

logger = logging.getLogger(__name__)

class VideoUtils:
    """
    Utility class for video processing operations.
    Provides helper functions for video file handling, format conversion, and analysis.
    """
    
    @staticmethod
    def get_video_info(video_path: str) -> dict:
        """
        Get comprehensive information about a video file.
        
        Args:
            video_path: Path to video file
            
        Returns:
            Dictionary containing video properties
        """
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
                'codec': '',
                'size_mb': 0
            }
            
            # Calculate duration
            if info['fps'] > 0:
                info['duration'] = info['frame_count'] / info['fps']
            
            # Get file size
            if os.path.exists(video_path):
                info['size_mb'] = os.path.getsize(video_path) / (1024 * 1024)
            
            # Try to get codec information
            fourcc = int(cap.get(cv2.CAP_PROP_FOURCC))
            if fourcc > 0:
                codec_bytes = fourcc.to_bytes(4, byteorder='little')
                try:
                    info['codec'] = codec_bytes.decode('ascii').strip('\x00')
                except UnicodeDecodeError:
                    info['codec'] = 'Unknown'
            
            cap.release()
            return info
            
        except Exception as e:
            logger.error(f"Error getting video info: {e}")
            return {}
    
    @staticmethod
    def is_valid_video(video_path: str) -> bool:
        """
        Check if a file is a valid video that can be opened.
        
        Args:
            video_path: Path to video file
            
        Returns:
            True if video is valid, False otherwise
        """
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
    def get_video_codecs() -> List[str]:
        """
        Get list of available video codecs for output.
        
        Returns:
            List of codec fourcc codes
        """
        # Common codecs that are usually available
        common_codecs = ['mp4v', 'XVID', 'MJPG', 'X264']
        available_codecs = []
        
        for codec in common_codecs:
            try:
                # Try to create a VideoWriter with this codec
                fourcc = cv2.VideoWriter_fourcc(*codec)
                test_path = 'test_codec.avi'
                writer = cv2.VideoWriter(test_path, fourcc, 30, (640, 480))
                
                if writer.isOpened():
                    available_codecs.append(codec)
                    writer.release()
                    
                    # Clean up test file
                    if os.path.exists(test_path):
                        os.remove(test_path)
                        
            except Exception:
                continue
        
        return available_codecs
    
    @staticmethod
    def extract_frames(video_path: str, output_dir: str, 
                      frame_interval: int = 1, max_frames: int = None) -> List[str]:
        """
        Extract frames from video as image files.
        
        Args:
            video_path: Path to input video
            output_dir: Directory to save extracted frames
            frame_interval: Extract every Nth frame (1 = all frames)
            max_frames: Maximum number of frames to extract
            
        Returns:
            List of paths to extracted frame images
        """
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
    def create_video_from_frames(frame_paths: List[str], output_path: str, 
                                fps: float = 30.0, codec: str = 'mp4v') -> bool:
        """
        Create video from a sequence of frame images.
        
        Args:
            frame_paths: List of paths to frame images
            output_path: Path for output video
            fps: Frames per second for output video
            codec: Video codec to use
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not frame_paths:
                raise ValueError("No frame paths provided")
            
            # Read first frame to get dimensions
            first_frame = cv2.imread(frame_paths[0])
            if first_frame is None:
                raise ValueError(f"Could not read first frame: {frame_paths[0]}")
            
            height, width = first_frame.shape[:2]
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*codec)
            writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            if not writer.isOpened():
                raise ValueError(f"Could not create video writer for {output_path}")
            
            # Write frames
            for frame_path in frame_paths:
                frame = cv2.imread(frame_path)
                if frame is not None:
                    # Resize frame if dimensions don't match
                    if frame.shape[:2] != (height, width):
                        frame = cv2.resize(frame, (width, height))
                    writer.write(frame)
            
            writer.release()
            logger.info(f"Created video: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Error creating video from frames: {e}")
            return False
    
    @staticmethod
    def resize_video(input_path: str, output_path: str, 
                    target_width: int, target_height: int = None, 
                    maintain_aspect: bool = True) -> bool:
        """
        Resize a video to new dimensions.
        
        Args:
            input_path: Path to input video
            output_path: Path for output video
            target_width: Target width in pixels
            target_height: Target height in pixels (optional)
            maintain_aspect: Whether to maintain aspect ratio
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cap = cv2.VideoCapture(input_path)
            if not cap.isOpened():
                raise ValueError(f"Could not open input video: {input_path}")
            
            # Get original dimensions
            orig_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            orig_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            fps = cap.get(cv2.CAP_PROP_FPS)
            
            # Calculate target dimensions
            if target_height is None or maintain_aspect:
                aspect_ratio = orig_width / orig_height
                if target_height is None:
                    target_height = int(target_width / aspect_ratio)
                else:
                    # Adjust width to maintain aspect ratio
                    target_width = int(target_height * aspect_ratio)
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(output_path, fourcc, fps, (target_width, target_height))
            
            if not writer.isOpened():
                raise ValueError(f"Could not create output video: {output_path}")
            
            # Process frames
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Resize frame
                resized_frame = cv2.resize(frame, (target_width, target_height))
                writer.write(resized_frame)
            
            cap.release()
            writer.release()
            
            logger.info(f"Resized video: {input_path} -> {output_path} ({target_width}x{target_height})")
            return True
            
        except Exception as e:
            logger.error(f"Error resizing video: {e}")
            return False
    
    @staticmethod
    def get_frame_at_time(video_path: str, time_seconds: float) -> Optional[np.ndarray]:
        """
        Extract a single frame at a specific time.
        
        Args:
            video_path: Path to video file
            time_seconds: Time in seconds to extract frame
            
        Returns:
            Frame as numpy array, or None if failed
        """
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
    
    @staticmethod
    def trim_video(input_path: str, output_path: str, 
                  start_time: float, end_time: float) -> bool:
        """
        Trim video to a specific time range.
        
        Args:
            input_path: Path to input video
            output_path: Path for output video
            start_time: Start time in seconds
            end_time: End time in seconds
            
        Returns:
            True if successful, False otherwise
        """
        try:
            cap = cv2.VideoCapture(input_path)
            if not cap.isOpened():
                raise ValueError(f"Could not open input video: {input_path}")
            
            # Get video properties
            fps = cap.get(cv2.CAP_PROP_FPS)
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            
            # Calculate frame numbers
            start_frame = int(start_time * fps)
            end_frame = int(end_time * fps)
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            writer = cv2.VideoWriter(output_path, fourcc, fps, (width, height))
            
            if not writer.isOpened():
                raise ValueError(f"Could not create output video: {output_path}")
            
            # Seek to start frame
            cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)
            
            # Write frames in range
            current_frame = start_frame
            while current_frame <= end_frame:
                ret, frame = cap.read()
                if not ret:
                    break
                
                writer.write(frame)
                current_frame += 1
            
            cap.release()
            writer.release()
            
            logger.info(f"Trimmed video: {input_path} -> {output_path} ({start_time}s-{end_time}s)")
            return True
            
        except Exception as e:
            logger.error(f"Error trimming video: {e}")
            return False
    
    @staticmethod
    def get_video_thumbnail(video_path: str, time_seconds: float = 1.0, 
                           size: Tuple[int, int] = (320, 240)) -> Optional[np.ndarray]:
        """
        Generate a thumbnail image from video.
        
        Args:
            video_path: Path to video file
            time_seconds: Time to extract thumbnail from
            size: Size of thumbnail (width, height)
            
        Returns:
            Thumbnail image as numpy array, or None if failed
        """
        try:
            frame = VideoUtils.get_frame_at_time(video_path, time_seconds)
            if frame is None:
                return None
            
            # Resize to thumbnail size
            thumbnail = cv2.resize(frame, size)
            return thumbnail
            
        except Exception as e:
            logger.error(f"Error generating thumbnail: {e}")
            return None