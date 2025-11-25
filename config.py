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

# Project paths
PROJECT_ROOT = Path(__file__).parent
MODELS_DIR = PROJECT_ROOT / "models"
LOGS_DIR = PROJECT_ROOT / "logs"

# Create directories
MODELS_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)

# ============================================================================
# Performance Settings
# ============================================================================

# Face detection scale (smaller = faster, less accurate)
FACE_DETECTION_SCALE = 0.5

# Face recognition similarity threshold
FACE_RECOGNITION_THRESHOLD = 0.6

# Video processing settings
SCAN_FRAME_SKIP = 10
OUTPUT_VIDEO_CODEC = 'mp4v'

# Create output directory
OUTPUT_VIDEO_DIR = Path.home() / "Videos" / "FaceSwap"
OUTPUT_VIDEO_DIR.mkdir(parents=True, exist_ok=True)

# ============================================================================
# Face Swapping Settings
# ============================================================================

# Blending settings
try:
    import cv2
    BLEND_METHOD = cv2.NORMAL_CLONE
except ImportError:
    BLEND_METHOD = 'NORMAL_CLONE'

MASK_FEATHER_AMOUNT = 6

# Smoothing settings
SMOOTHING_METHOD = 'one_euro'
SMOOTHING_PARAMS = {
    'one_euro': {
        'freq': 30.0,
        'min_cutoff': 1.0,
        'beta': 0.002,
        'd_cutoff': 1.0
    },
    'ema': {
        'alpha': 0.4
    }
}

# Color correction
ENABLE_COLOR_MATCHING = True
COLOR_CORRECTION_STRENGTH = 0.7

# ============================================================================
# File Settings
# ============================================================================

# Model files
FACE_LANDMARKS_MODEL = MODELS_DIR / "shape_predictor_68_face_landmarks.dat"
FACE_RECOGNITION_MODEL = MODELS_DIR / "dlib_face_recognition_resnet_model_v1.dat"

# Supported formats
SUPPORTED_VIDEO_FORMATS = [".mp4", ".avi", ".mov", ".mkv", ".wmv"]
SUPPORTED_IMAGE_FORMATS = [".jpg", ".jpeg", ".png", ".bmp"]

# ============================================================================
# GUI Settings
# ============================================================================

MAIN_WINDOW_WIDTH = 1000
MAIN_WINDOW_HEIGHT = 700
FACE_CARD_WIDTH = 220
FACE_CARD_HEIGHT = 300

# ============================================================================
# Logging Settings
# ============================================================================

LOG_LEVEL = "INFO"
LOG_FILE_PATH = LOGS_DIR / "faceswap.log"
