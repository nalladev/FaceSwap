import pytest
import os
import numpy as np
import cv2
from pathlib import Path
import tempfile
import shutil

@pytest.fixture(scope="session")
def test_data_dir():
    """Create a temporary directory with test images."""
    temp_dir = tempfile.mkdtemp(prefix="faceswap_test_")
    
    # Create sample test images
    create_test_images(temp_dir)
    
    yield temp_dir
    
    # Cleanup
    shutil.rmtree(temp_dir)

@pytest.fixture
def sample_face_image():
    """Generate a sample image with a face-like pattern."""
    img = np.zeros((400, 400, 3), dtype=np.uint8)
    # Draw a simple face-like pattern
    cv2.circle(img, (200, 200), 150, (255, 255, 255), -1)  # Face
    cv2.circle(img, (170, 170), 20, (0, 0, 0), -1)  # Left eye
    cv2.circle(img, (230, 170), 20, (0, 0, 0), -1)  # Right eye
    cv2.ellipse(img, (200, 220), (30, 20), 0, 0, 180, (0, 0, 0), 2)  # Mouth
    return img

@pytest.fixture
def empty_image():
    """Generate an empty image with no faces."""
    return np.zeros((300, 300, 3), dtype=np.uint8)

@pytest.fixture
def output_dir():
    """Create a temporary output directory."""
    temp_dir = tempfile.mkdtemp(prefix="faceswap_output_")
    yield temp_dir
    shutil.rmtree(temp_dir)

def create_test_images(directory):
    """Create various test images for different test scenarios."""
    # Single face image
    single_face = np.zeros((400, 400, 3), dtype=np.uint8)
    cv2.circle(single_face, (200, 200), 150, (255, 255, 255), -1)
    cv2.circle(single_face, (170, 170), 20, (0, 0, 0), -1)
    cv2.circle(single_face, (230, 170), 20, (0, 0, 0), -1)
    cv2.imwrite(os.path.join(directory, "single_face.jpg"), single_face)
    
    # Multiple faces image
    multi_face = np.zeros((400, 600, 3), dtype=np.uint8)
    # Face 1
    cv2.circle(multi_face, (150, 200), 100, (255, 255, 255), -1)
    cv2.circle(multi_face, (130, 180), 15, (0, 0, 0), -1)
    cv2.circle(multi_face, (170, 180), 15, (0, 0, 0), -1)
    # Face 2
    cv2.circle(multi_face, (450, 200), 100, (255, 255, 255), -1)
    cv2.circle(multi_face, (430, 180), 15, (0, 0, 0), -1)
    cv2.circle(multi_face, (470, 180), 15, (0, 0, 0), -1)
    cv2.imwrite(os.path.join(directory, "multi_face.jpg"), multi_face)
    
    # No face image
    no_face = np.random.randint(0, 255, (300, 300, 3), dtype=np.uint8)
    cv2.imwrite(os.path.join(directory, "no_face.jpg"), no_face)
    
    # Corrupted image (text file with jpg extension)
    with open(os.path.join(directory, "corrupted.jpg"), "w") as f:
        f.write("This is not an image")
