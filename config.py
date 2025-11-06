"""
Configuration file for FaceSwap application.

This module contains all configurable parameters for the face detection,
recognition, and swapping processes. Adjust these values to optimize
performance vs quality trade-offs.
"""

import os
from pathlib import Path

# ============================================================================
# Application Configuration
# ============================================================================

APP_NAME = "FaceSwap"
APP_VERSION = "1.0.1"
APP_DESCRIPTION = "Local Face Swapping Tool"

# Project paths
PROJECT_ROOT = Path(__file__).parent
MODELS_DIR = PROJECT_ROOT / "models"
ASSETS_DIR = PROJECT_ROOT / "assets"
LOGS_DIR = PROJECT_ROOT / "logs"

# Create directories if they don't exist
MODELS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# ============================================================================
# Face Detection Configuration
# ============================================================================

# Face detection scale factor (smaller = faster detection, less accurate)
# Values: 0.1 - 1.0
# 1.0 = full resolution (highest quality, slowest)
# 0.5 = half resolution (good balance)
# 0.3 = fast detection (lower quality, fastest)
FACE_DETECTION_SCALE = 0.5

# Minimum face size for detection (in pixels)
MIN_FACE_SIZE = 50

# Maximum face size for detection (in pixels, 0 = no limit)
MAX_FACE_SIZE = 0

# Face detection confidence threshold
FACE_DETECTION_CONFIDENCE = 0.5

# ============================================================================
# Face Recognition Configuration
# ============================================================================

# Face recognition similarity threshold
# Lower values = stricter matching (fewer false positives)
# Higher values = looser matching (more faces grouped together)
# Typical range: 0.4 - 0.8
FACE_RECOGNITION_THRESHOLD = 0.6

# Maximum number of unique faces to detect
# Set to 0 for no limit
MAX_UNIQUE_FACES = 20

# ============================================================================
# Video Processing Configuration
# ============================================================================

# Frame skip interval for face scanning
# Process every Nth frame (higher = faster scanning, might miss faces)
SCAN_FRAME_SKIP = 10

# Video processing frame skip
# Process every Nth frame for swapping (higher = faster, less smooth)
PROCESS_FRAME_SKIP = 1

# Output video quality
# Higher values = better quality, larger file size
OUTPUT_VIDEO_QUALITY = 90

# Default output video codec
OUTPUT_VIDEO_CODEC = 'mp4v'

# Output video directory
OUTPUT_VIDEO_DIR = Path.home() / "Videos"

# ============================================================================
# Face Swapping Configuration
# ============================================================================

# Blending method for face swapping
# Options: cv2.NORMAL_CLONE, cv2.MIXED_CLONE, cv2.MONOCHROME_TRANSFER
import cv2
BLEND_METHOD = cv2.NORMAL_CLONE

# Face mask feathering amount (pixels)
# Higher values = smoother blending, more processing time
MASK_FEATHER_AMOUNT = 6

# Color correction strength (0.0 - 1.0)
# 0.0 = no color correction
# 1.0 = full color matching
COLOR_CORRECTION_STRENGTH = 0.7

# Face alignment method
# 'simple' = basic 3-point alignment (faster)
# 'full' = full 68-point alignment (better quality)
ALIGNMENT_METHOD = 'simple'

# ============================================================================
# GUI Configuration
# ============================================================================

# Main window size
MAIN_WINDOW_WIDTH = 1000
MAIN_WINDOW_HEIGHT = 700

# Face card size in pixels
FACE_CARD_WIDTH = 220
FACE_CARD_HEIGHT = 300

# Face cards per row in grid
FACE_CARDS_PER_ROW = 4

# Progress dialog update interval (milliseconds)
PROGRESS_UPDATE_INTERVAL = 100

# ============================================================================
# Performance Configuration
# ============================================================================

# Number of threads for parallel processing
# 0 = auto-detect based on CPU cores
# >0 = specific number of threads
NUM_THREADS = 0

# Memory optimization settings
# Enable memory optimization for large videos
ENABLE_MEMORY_OPTIMIZATION = True

# Maximum frames to keep in memory at once
MAX_FRAMES_IN_MEMORY = 100

# Enable GPU acceleration if available
ENABLE_GPU_ACCELERATION = False

# ============================================================================
# Logging Configuration
# ============================================================================

# Logging level
# Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = "INFO"

# Log file settings
LOG_FILE_PATH = LOGS_DIR / "faceswap.log"
LOG_MAX_SIZE_MB = 10
LOG_BACKUP_COUNT = 5

# Enable console logging
ENABLE_CONSOLE_LOGGING = True

# ============================================================================
# Model Configuration
# ============================================================================

# Required model files
REQUIRED_MODELS = {
    "face_landmarks": {
        "filename": "shape_predictor_68_face_landmarks.dat",
        "url": "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2",
        "description": "68-point facial landmark predictor"
    },
    "face_recognition": {
        "filename": "dlib_face_recognition_resnet_model_v1.dat",
        "url": "http://dlib.net/files/dlib_face_recognition_resnet_model_v1.dat.bz2",
        "description": "Face recognition model"
    }
}

# Model file paths
FACE_LANDMARKS_MODEL = MODELS_DIR / REQUIRED_MODELS["face_landmarks"]["filename"]
FACE_RECOGNITION_MODEL = MODELS_DIR / REQUIRED_MODELS["face_recognition"]["filename"]

# ============================================================================
# File Format Configuration
# ============================================================================

# Supported video formats for input
SUPPORTED_VIDEO_FORMATS = [
    ".mp4", ".avi", ".mov", ".mkv", ".wmv", ".flv", ".webm", ".m4v"
]

# Supported image formats for swap images
SUPPORTED_IMAGE_FORMATS = [
    ".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif", ".webp"
]

# Default file extensions
DEFAULT_VIDEO_EXTENSION = ".mp4"
DEFAULT_IMAGE_EXTENSION = ".jpg"

# ============================================================================
# Advanced Configuration
# ============================================================================

# Enable experimental features
ENABLE_EXPERIMENTAL_FEATURES = False

# Debug mode settings
DEBUG_MODE = False
DEBUG_SAVE_INTERMEDIATE_IMAGES = False
DEBUG_OUTPUT_DIR = PROJECT_ROOT / "debug_output"

# Profiling settings
ENABLE_PROFILING = False
PROFILE_OUTPUT_DIR = PROJECT_ROOT / "profiling"

# ============================================================================
# Quality Presets
# ============================================================================

QUALITY_PRESETS = {
    "fast": {
        "FACE_DETECTION_SCALE": 0.3,
        "SCAN_FRAME_SKIP": 20,
        "PROCESS_FRAME_SKIP": 2,
        "MASK_FEATHER_AMOUNT": 3,
        "ALIGNMENT_METHOD": "simple"
    },
    "balanced": {
        "FACE_DETECTION_SCALE": 0.5,
        "SCAN_FRAME_SKIP": 10,
        "PROCESS_FRAME_SKIP": 1,
        "MASK_FEATHER_AMOUNT": 6,
        "ALIGNMENT_METHOD": "simple"
    },
    "high_quality": {
        "FACE_DETECTION_SCALE": 1.0,
        "SCAN_FRAME_SKIP": 5,
        "PROCESS_FRAME_SKIP": 1,
        "MASK_FEATHER_AMOUNT": 10,
        "ALIGNMENT_METHOD": "full"
    }
}

# Default quality preset
DEFAULT_QUALITY_PRESET = "balanced"

# ============================================================================
# Helper Functions
# ============================================================================

def apply_quality_preset(preset_name: str):
    """
    Apply a quality preset configuration.

    Args:
        preset_name: Name of the preset to apply
    """
    if preset_name not in QUALITY_PRESETS:
        raise ValueError(f"Unknown quality preset: {preset_name}")

    preset = QUALITY_PRESETS[preset_name]
    globals().update(preset)

def get_model_path(model_name: str) -> Path:
    """
    Get the full path to a model file.

    Args:
        model_name: Name of the model (from REQUIRED_MODELS keys)

    Returns:
        Path to the model file
    """
    if model_name not in REQUIRED_MODELS:
        raise ValueError(f"Unknown model: {model_name}")

    filename = REQUIRED_MODELS[model_name]["filename"]
    return MODELS_DIR / filename

def validate_config():
    """
    Validate configuration values and fix any issues.
    """
    global FACE_DETECTION_SCALE, FACE_RECOGNITION_THRESHOLD
    global MASK_FEATHER_AMOUNT, COLOR_CORRECTION_STRENGTH

    # Clamp values to valid ranges
    FACE_DETECTION_SCALE = max(0.1, min(1.0, FACE_DETECTION_SCALE))
    FACE_RECOGNITION_THRESHOLD = max(0.1, min(1.0, FACE_RECOGNITION_THRESHOLD))
    MASK_FEATHER_AMOUNT = max(0, min(20, MASK_FEATHER_AMOUNT))
    COLOR_CORRECTION_STRENGTH = max(0.0, min(1.0, COLOR_CORRECTION_STRENGTH))

# Validate configuration on import
validate_config()
