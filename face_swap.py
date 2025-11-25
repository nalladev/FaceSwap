import cv2
import numpy as np
import torch
import torch.nn.functional as F
from utils.gpu_utils import gpu_manager
import logging

logger = logging.getLogger(__name__)

class FaceSwapper:
    def __init__(self):
        self.device = gpu_manager.device
        self.batch_size = gpu_manager.get_optimal_batch_size()
        
    def swap_faces_gpu(self, source_image: np.ndarray, target_image: np.ndarray, 
                      source_face: tuple, target_face: tuple) -> np.ndarray:
        """GPU-accelerated face swapping."""
        try:
            # Convert to tensors and move to GPU
            source_tensor = self._image_to_tensor(source_image).to(self.device)
            target_tensor = self._image_to_tensor(target_image).to(self.device)
            
            # Extract face regions
            source_face_tensor = self._extract_face_tensor(source_tensor, source_face)
            target_face_tensor = self._extract_face_tensor(target_tensor, target_face)
            
            # Perform GPU-accelerated blending and transformation
            swapped_face = self._blend_faces_gpu(source_face_tensor, target_face_tensor)
            
            # Insert back into target image
            result = self._insert_face_gpu(target_tensor, swapped_face, target_face)
            
            # Convert back to numpy
            return self._tensor_to_image(result)
            
        except Exception as e:
            logger.warning(f"GPU face swap failed: {e}, falling back to CPU")
            return self.swap_faces_cpu(source_image, target_image, source_face, target_face)
    
    def _image_to_tensor(self, image: np.ndarray) -> torch.Tensor:
        """Convert numpy image to tensor."""
        # Convert BGR to RGB and normalize
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        tensor = torch.from_numpy(image_rgb).float() / 255.0
        return tensor.permute(2, 0, 1).unsqueeze(0)  # CHW format with batch dimension
    
    def _tensor_to_image(self, tensor: torch.Tensor) -> np.ndarray:
        """Convert tensor back to numpy image."""
        # Move to CPU and convert
        image = tensor.squeeze(0).permute(1, 2, 0).cpu().numpy()
        image = (image * 255).astype(np.uint8)
        return cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    
    def _extract_face_tensor(self, image_tensor: torch.Tensor, face_coords: tuple) -> torch.Tensor:
        """Extract face region as tensor."""
        x, y, w, h = face_coords
        return image_tensor[:, :, y:y+h, x:x+w]
    
    def _blend_faces_gpu(self, source_face: torch.Tensor, target_face: torch.Tensor) -> torch.Tensor:
        """GPU-accelerated face blending."""
        # Resize source face to match target face size
        target_size = (target_face.shape[2], target_face.shape[3])
        source_resized = F.interpolate(source_face, size=target_size, mode='bilinear', align_corners=False)
        
        # Create blending mask using GPU operations
        mask = self._create_blending_mask_gpu(target_size)
        
        # Perform blending
        blended = source_resized * mask + target_face * (1 - mask)
        
        return blended
    
    def _create_blending_mask_gpu(self, size: tuple) -> torch.Tensor:
        """Create a smooth blending mask on GPU."""
        h, w = size
        center_x, center_y = w // 2, h // 2
        
        # Create coordinate grids
        y, x = torch.meshgrid(torch.arange(h, device=self.device), 
                             torch.arange(w, device=self.device), indexing='ij')
        
        # Calculate distance from center
        dist = torch.sqrt((x - center_x)**2 + (y - center_y)**2)
        
        # Create soft circular mask
        radius = min(w, h) // 3
        mask = torch.clamp(1.0 - dist / radius, 0, 1)
        
        # Add batch and channel dimensions
        return mask.unsqueeze(0).unsqueeze(0).repeat(1, 3, 1, 1)
    
    def _insert_face_gpu(self, target_image: torch.Tensor, face: torch.Tensor, 
                        face_coords: tuple) -> torch.Tensor:
        """Insert blended face back into target image."""
        x, y, w, h = face_coords
        result = target_image.clone()
        
        # Resize face to exact coordinates
        face_resized = F.interpolate(face, size=(h, w), mode='bilinear', align_corners=False)
        
        # Insert face
        result[:, :, y:y+h, x:x+w] = face_resized
        
        return result
    
    def swap_faces_cpu(self, source_image: np.ndarray, target_image: np.ndarray,
                      source_face: tuple, target_face: tuple) -> np.ndarray:
        """CPU fallback for face swapping with GPU preprocessing."""
        # Use GPU for image preprocessing if available
        source_processed = gpu_manager.optimize_image_processing(source_image)
        target_processed = gpu_manager.optimize_image_processing(target_image)
        
        # ...existing CPU face swap code...
        # Extract faces
        x1, y1, w1, h1 = source_face
        x2, y2, w2, h2 = target_face
        
        source_face_img = source_processed[y1:y1+h1, x1:x1+w1]
        target_face_img = target_processed[y2:y2+h2, x2:x2+w2]
        
        # Resize source face to match target face
        source_face_resized = cv2.resize(source_face_img, (w2, h2))
        
        # Create seamless clone
        center = (x2 + w2//2, y2 + h2//2)
        mask = 255 * np.ones(source_face_resized.shape, source_face_resized.dtype)
        
        result = cv2.seamlessClone(source_face_resized, target_processed, mask, center, cv2.NORMAL_CLONE)
        
        return result
    
    def swap_faces(self, source_image: np.ndarray, target_image: np.ndarray,
                  source_face: tuple, target_face: tuple) -> np.ndarray:
        """Main face swapping method that chooses optimal approach."""
        if self.device.type in ['cuda', 'mps']:
            return self.swap_faces_gpu(source_image, target_image, source_face, target_face)
        else:
            return self.swap_faces_cpu(source_image, target_image, source_face, target_face)
