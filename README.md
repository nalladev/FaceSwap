# FaceSwap - Local Face Swapping Tool

[![Build Status](https://github.com/ZacharyJoyner/faceswap/workflows/Build%20and%20Release%20FaceSwap/badge.svg)](https://github.com/ZacharyJoyner/faceswap/actions)
[![Linux Build](https://github.com/ZacharyJoyner/faceswap/workflows/Build%20FaceSwap%20with%20Conda%20(Alternative)/badge.svg)](https://github.com/ZacharyJoyner/faceswap/actions)

A powerful, local face swapping application built with Python, OpenCV, and Dlib. This tool allows you to swap faces in videos using advanced computer vision techniques, all running locally on your machine without any cloud dependencies.

## ⬇️ Download & Install

### 🚀 For End Users (Recommended)

**Just want to use the app? Download the pre-built executable:**

#### Windows
1. **Download**: [FaceSwap-Windows-x64.zip](https://github.com/ZacharyJoyner/faceswap/releases/latest/download/FaceSwap-Windows-x64.zip)
2. **Extract** the ZIP file to any folder
3. **Run** `FaceSwap.exe`
4. **That's it!** No Python installation needed.

#### Linux  
1. **Download**: [FaceSwap-Linux-x64.tar.gz](https://github.com/ZacharyJoyner/faceswap/releases/latest/download/FaceSwap-Linux-x64.tar.gz)
2. **Extract**: `tar -xzf FaceSwap-Linux-x64.tar.gz`
3. **Run**: `./FaceSwap/FaceSwap`
4. **Optional**: Make executable: `chmod +x FaceSwap/FaceSwap`

#### macOS
*Coming soon! For now, use the Developer Installation method below.*

### 💻 For Developers

If you want to modify the code or run from source:

#### Prerequisites
1. **Python 3.9** installed on your system
2. **Git** for cloning the repository

#### Installation Steps
```bash
# Clone the repository
git clone https://github.com/ZacharyJoyner/faceswap.git
cd faceswap

# Install Python dependencies
pip install -r requirements.txt

# Download required AI models
python -c "
import urllib.request
import bz2
import os

os.makedirs('models', exist_ok=True)

# Download and extract shape predictor
print('Downloading face landmark model...')
urllib.request.urlretrieve(
    'http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2',
    'models/shape_predictor_68_face_landmarks.dat.bz2'
)
with bz2.BZ2File('models/shape_predictor_68_face_landmarks.dat.bz2', 'rb') as f_in:
    with open('models/shape_predictor_68_face_landmarks.dat', 'wb') as f_out:
        f_out.write(f_in.read())

# Download and extract face recognition model
print('Downloading face recognition model...')
urllib.request.urlretrieve(
    'http://dlib.net/files/dlib_face_recognition_resnet_model_v1.dat.bz2',
    'models/dlib_face_recognition_resnet_model_v1.dat.bz2'
)
with bz2.BZ2File('models/dlib_face_recognition_resnet_model_v1.dat.bz2', 'rb') as f_in:
    with open('models/dlib_face_recognition_resnet_model_v1.dat', 'wb') as f_out:
        f_out.write(f_in.read())

print('Models downloaded successfully!')
"

# Test installation (optional but recommended)
python -c "
import dlib
import cv2
import numpy as np
from PySide6 import QtCore, QtGui, QtWidgets
print('✓ All dependencies installed successfully')
"

# Run the application
python main.py
```

### 🛠️ For Developers/Contributors

If you want to trigger a manual build or test the CI/CD system:

#### Manual Build Trigger
1. Go to the **Actions** tab in the GitHub repository
2. Select **"Build and Release FaceSwap"** workflow
3. Click **"Run workflow"** button
4. Enter a version tag (e.g., `v1.0.0-test`)
5. Click **"Run workflow"** to start the build

## Features

- **🔒 100% Local Processing**: Everything runs on your machine - no internet required after setup
- **🎯 Automatic Face Detection**: Detects and groups unique faces in videos using dlib
- **🖥️ Interactive GUI**: Easy-to-use interface built with PySide6
- **✨ High Quality Results**: Uses Poisson blending for seamless face swaps
- **📊 Progress Tracking**: Real-time progress updates during processing
- **🚫 No Cloud Dependencies**: Your videos never leave your computer

## Tech Stack

- **Language**: Python 3.9
- **GUI Framework**: PySide6 (Qt for Python)
- **Computer Vision**: OpenCV 4.8.1, Dlib 19.24.2
- **Math/Arrays**: NumPy 1.24.3
- **Image Processing**: Pillow 10.0.1

## 🎬 How to Use

### Quick Start Guide

1. **Launch** the FaceSwap application (`python main.py`)
2. **Select Video**: Click "Select Video" to choose your input video file
3. **Scan for Faces**: Click "Scan Video for Faces" to detect all unique people (this may take a few minutes)
4. **Assign Swap Images**: For each detected face, click "Select Image..." to choose a replacement face image
5. **Process Video**: Click "Process Video" to generate the face-swapped video
6. **Done!**: Find your swapped video in `~/Videos/faceswap_output.mp4`

### 📁 Supported Formats

- **Input Video**: MP4, AVI, MOV, MKV, WMV, FLV, WebM
- **Swap Images**: JPG, JPEG, PNG, BMP, TIFF, WebP

### 💡 Tips for Best Results

- **High-quality source images**: Use clear, well-lit photos of faces
- **Similar angles**: Source images should have similar face angles to the video
- **Good lighting**: Both video and swap images should have decent lighting
- **Face size**: Larger faces in the video work better than tiny distant faces

## How It Works

### Face Detection Pipeline

1. **Frame Analysis**: The application analyzes each frame of the video
2. **Face Detection**: Uses Dlib's frontal face detector to find faces
3. **Landmark Extraction**: Identifies 68 facial landmarks for each face
4. **Face Encoding**: Generates 128-dimensional face embeddings
5. **Face Clustering**: Groups similar faces together as unique individuals

### Face Swapping Process

1. **Landmark Alignment**: Maps facial landmarks between source and target faces
2. **Affine Transformation**: Calculates transformation matrix for face warping
3. **Face Warping**: Applies transformation to align the swap face
4. **Mask Generation**: Creates precise face mask for seamless blending
5. **Poisson Blending**: Uses OpenCV's seamless cloning for natural results

## Project Structure

```
FaceSwap/
├── main.py                 # Main application entry point
├── face_detector.py        # Face detection and recognition logic
├── face_swapper.py         # Face swapping algorithms
├── gui/
│   ├── __init__.py
│   ├── main_window.py      # Main GUI window
│   ├── face_card.py        # Individual face card widget
│   └── progress_dialog.py  # Progress tracking dialog
├── utils/
│   ├── __init__.py
│   └── video_utils.py      # Video processing utilities
├── models/                 # Dlib model files (auto-downloaded)
├── requirements.txt        # Python dependencies
├── config.py              # Configuration settings
└── README.md              # This file
```

## Configuration

### Performance Settings

You can adjust these parameters in `config.py`:

- `FACE_DETECTION_SCALE`: Resize factor for faster detection (default: 0.5)
- `FACE_RECOGNITION_THRESHOLD`: Similarity threshold for face matching (default: 0.6)
- `BLEND_METHOD`: Blending algorithm (default: cv2.NORMAL_CLONE)

### Quality vs Speed

- **High Quality**: Use full resolution (`FACE_DETECTION_SCALE = 1.0`)
- **Fast Processing**: Use lower resolution (`FACE_DETECTION_SCALE = 0.3`)

## System Requirements

### Minimum Requirements
- **OS**: Windows 10+, Ubuntu 18.04+, or macOS 10.14+
- **RAM**: 4GB minimum, 8GB recommended
- **CPU**: Multi-core processor (Intel i5 or AMD Ryzen 5 equivalent)
- **Storage**: 2GB free space
- **GPU**: Not required (CPU-only processing)

### Recommended Specs
- **RAM**: 16GB for processing large videos
- **CPU**: Intel i7 or AMD Ryzen 7 for faster processing
- **SSD**: For better performance with large video files

## 🔧 Troubleshooting

### Pre-built Executable Issues

1. **"Windows protected your PC" warning**:
   - Click "More info" → "Run anyway"
   - This is normal for unsigned executables

2. **Linux: "Permission denied"**:
   ```bash
   chmod +x FaceSwap/FaceSwap
   ./FaceSwap/FaceSwap
   ```

3. **Application won't start**:
   - Check system requirements above
   - Try running from terminal to see error messages
   - Ensure you extracted all files from the archive

### Developer Installation Issues

1. **Dlib compilation fails**:
   ```bash
   # Install system dependencies first
   sudo apt-get install build-essential cmake libopenblas-dev liblapack-dev
   pip install dlib --no-cache-dir
   ```

2. **Model download fails**:
   - Check internet connection
   - Manually download models from http://dlib.net/files/
   - Place in `models/` directory

3. **Import errors**:
   ```bash
   # Test each dependency individually
   python -c "import dlib; print('✓ Dlib works')"
   python -c "import cv2; print('✓ OpenCV works')"
   python -c "from PySide6 import QtWidgets; print('✓ PySide6 works')"
   ```

### Video Processing Issues

1. **Video not opening**:
   - Try converting to MP4 format first
   - Ensure video file isn't corrupted
   - Check that video has actual faces visible

2. **Slow processing**:
   - Close other applications to free up CPU
   - Use shorter video clips for testing
   - Lower resolution videos process faster

3. **Poor quality results**:
   - Use high-quality source images (1080p+)
   - Ensure good lighting in both video and swap images
   - Try different source images with similar face angles

### Getting Help

- **GitHub Issues**: Report bugs at [GitHub Issues](https://github.com/ZacharyJoyner/faceswap/issues)
- **System Info**: Include your OS, RAM, and video details when reporting issues

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

### Development Setup

```bash
# Clone for development
git clone https://github.com/ZacharyJoyner/faceswap.git
cd faceswap

# Install in development mode
pip install -r requirements.txt

# Install development dependencies (optional)
pip install pytest black flake8
```

## 📊 Performance Expectations

### Processing Times (approximate)
- **1-minute 1080p video**: 5-15 minutes on modern CPU
- **Face detection**: 1-5 minutes depending on video length
- **Large videos (>10 min)**: Consider splitting into smaller chunks

### Memory Usage
- **Basic operation**: 2-4GB RAM
- **Large videos**: Up to 8GB RAM
- **Background apps**: Close unnecessary programs during processing

## 🔄 Updates & Releases

This application uses GitHub Releases for distribution:

- **Automatic Updates**: Not yet available - check releases page manually
- **Release Notes**: Each release includes detailed changelog
- **Beta Versions**: Available for testing new features
- **Manual Builds**: Contributors can trigger builds manually via GitHub Actions

### Build Status
- **Main Build** (pip-based): For most users and systems
- **Manual Triggers**: Available for testing and development

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Dlib**: Davis King's machine learning library for face detection
- **OpenCV**: Open Source Computer Vision Library for image processing
- **Qt/PySide6**: Cross-platform GUI toolkit for the user interface
- **PyInstaller**: For creating standalone executables

## ⚠️ Important Disclaimer

**This tool is for educational, creative, and entertainment purposes only.**

- 🔐 **Privacy**: Your videos are processed locally and never uploaded anywhere
- ⚖️ **Legal**: Ensure you have permission to use any faces or videos you process
- 🤝 **Ethics**: Be mindful of consent when creating face-swapped content
- 🚫 **Misuse**: Do not use for creating misleading or harmful content
- 📋 **Responsibility**: Users are responsible for how they use this tool

**Use responsibly and respect others' privacy and consent.**