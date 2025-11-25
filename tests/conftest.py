import pytest
import os
import numpy as np
import cv2
from pathlib import Path
import tempfile
import shutil
import sys

# Add project root to path
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

@pytest.fixture
def synthetic_face_image():
    """Generate a synthetic face image for testing."""
    img = np.zeros((200, 200, 3), dtype=np.uint8)
    # Draw face-like pattern
    cv2.circle(img, (100, 100), 70, (200, 200, 200), -1)  # Face
    cv2.circle(img, (85, 85), 8, (0, 0, 0), -1)   # Left eye
    cv2.circle(img, (115, 85), 8, (0, 0, 0), -1)  # Right eye
    cv2.ellipse(img, (100, 110), (15, 8), 0, 0, 180, (0, 0, 0), 2)  # Mouth
    return img

@pytest.fixture
def multi_face_image():
    """Generate image with multiple faces."""
    img = np.zeros((200, 300, 3), dtype=np.uint8)
    # Face 1
    cv2.circle(img, (75, 100), 50, (200, 200, 200), -1)
    cv2.circle(img, (65, 85), 6, (0, 0, 0), -1)
    cv2.circle(img, (85, 85), 6, (0, 0, 0), -1)
    # Face 2
    cv2.circle(img, (225, 100), 50, (200, 200, 200), -1)
    cv2.circle(img, (215, 85), 6, (0, 0, 0), -1)
    cv2.circle(img, (235, 85), 6, (0, 0, 0), -1)
    return img

@pytest.fixture
def empty_image():
    """Generate empty image with no faces."""
    return np.zeros((200, 200, 3), dtype=np.uint8)

@pytest.fixture
def temp_output_dir():
    """Create temporary output directory."""
    temp_dir = Path(tempfile.mkdtemp(prefix="faceswap_test_"))
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture(scope="session")
def test_data_dir():
    """Create session-level test data directory."""
    temp_dir = Path(tempfile.mkdtemp(prefix="faceswap_session_"))
    yield temp_dir
    shutil.rmtree(temp_dir, ignore_errors=True)

@pytest.fixture
def sample_face_image():
    """Create a sample face image for testing."""
    # Create a more realistic face-like image
    image = np.zeros((300, 300, 3), dtype=np.uint8)
    
    # Add face-like features (simple geometric shapes)
    # Face outline (circle)
    cv2.circle(image, (150, 150), 100, (200, 180, 160), -1)
    
    # Eyes
    cv2.circle(image, (120, 120), 15, (255, 255, 255), -1)
    cv2.circle(image, (180, 120), 15, (255, 255, 255), -1)
    cv2.circle(image, (120, 120), 8, (0, 0, 0), -1)
    cv2.circle(image, (180, 120), 8, (0, 0, 0), -1)
    
    # Nose
    cv2.circle(image, (150, 160), 8, (180, 160, 140), -1)
    
    # Mouth
    cv2.ellipse(image, (150, 190), (20, 10), 0, 0, 180, (100, 50, 50), -1)
    
    return image

@pytest.fixture
def output_dir(tmp_path):
    """Create a temporary output directory for tests."""
    output_path = tmp_path / "output"
    output_path.mkdir()
    return str(output_path)

# Pytest configuration
def pytest_configure(config):
    """Configure pytest settings."""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "gpu: marks tests as requiring GPU")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")

def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers automatically."""
    for item in items:
        # Mark slow tests
        if "stress" in item.name.lower() or "memory" in item.name.lower():
            item.add_marker(pytest.mark.slow)
        
        # Mark integration tests
        if "integration" in item.name.lower() or "pipeline" in item.name.lower():
            item.add_marker(pytest.mark.integration)
