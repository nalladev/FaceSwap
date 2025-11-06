# FaceSwap - Local Face Swapping Tool

A powerful, local face swapping application built with Python, OpenCV, and Dlib. This tool allows you to swap faces in videos using advanced computer vision techniques, all running locally on your machine without any cloud dependencies.

## Features

- **Local Processing**: Everything runs on your machine - no internet required
- **Automatic Face Detection**: Detects and groups unique faces in videos
- **Interactive GUI**: Easy-to-use interface built with PySide6
- **High Quality Results**: Uses Poisson blending for seamless face swaps
- **Batch Processing**: Swap multiple faces in a single video
- **Progress Tracking**: Real-time progress updates during processing

## Tech Stack

- **Language**: Python 3.8+
- **GUI Framework**: PySide6 (Qt for Python)
- **Computer Vision**: OpenCV, Dlib
- **Math/Arrays**: NumPy
- **Image Processing**: Pillow

## Installation

### Prerequisites

1. **Python 3.8+** installed on your system
2. **CMake** (required for Dlib compilation)
3. **Visual Studio Build Tools** (Windows) or **build-essential** (Linux)

### Install Dependencies

```bash
# Clone the repository
git clone <repository-url>
cd FaceSwap

# Install Python dependencies
pip install -r requirements.txt
```

### Download Required Models

The application requires pre-trained Dlib models for face detection and recognition:

1. **Face Landmarks Predictor** (68-point model):
   - Download: [shape_predictor_68_face_landmarks.dat](http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2)
   - Extract and place in the `models/` directory

2. **Face Recognition Model**:
   - Download: [dlib_face_recognition_resnet_model_v1.dat](http://dlib.net/files/dlib_face_recognition_resnet_model_v1.dat.bz2)
   - Extract and place in the `models/` directory

```bash
# Create models directory
mkdir models

# Download and extract models (Linux/Mac)
wget http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
wget http://dlib.net/files/dlib_face_recognition_resnet_model_v1.dat.bz2

bzip2 -d shape_predictor_68_face_landmarks.dat.bz2
bzip2 -d dlib_face_recognition_resnet_model_v1.dat.bz2

mv *.dat models/
```

## Usage

### Running the Application

```bash
python main.py
```

### Step-by-Step Guide

1. **Select Video**: Click "Select Video" to choose your input video file
2. **Scan for Faces**: Click "Scan Video for Faces" to detect all unique faces
3. **Assign Swap Images**: For each detected face, click "Select Image..." to choose a replacement face image
4. **Process Video**: Click "Process Video" to generate the face-swapped video
5. **Save Result**: The processed video will be saved to `~/Videos/faceswap_output.mp4`

### Supported Formats

- **Input Video**: MP4, AVI, MOV, MKV
- **Swap Images**: JPG, PNG, BMP, TIFF

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
├── models/                 # Dlib model files (user downloads)
├── utils/
│   ├── __init__.py
│   └── video_utils.py      # Video processing utilities
├── requirements.txt        # Python dependencies
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

## Troubleshooting

### Common Issues

1. **Dlib Installation Fails**:
   - Install CMake: `pip install cmake`
   - Install build tools for your platform

2. **Models Not Found**:
   - Ensure model files are in the `models/` directory
   - Check file names match exactly

3. **Video Not Opening**:
   - Install additional codecs: `pip install opencv-contrib-python`
   - Try converting video to MP4 format

4. **Poor Quality Results**:
   - Use higher resolution source images
   - Ensure good lighting in both source and target
   - Adjust `FACE_RECOGNITION_THRESHOLD`

### Performance Tips

- **CPU Usage**: The application is CPU-intensive. Close other applications for better performance
- **Memory Usage**: Large videos may require significant RAM. Consider processing shorter clips
- **Speed**: Face detection is the bottleneck. Reduce `FACE_DETECTION_SCALE` for faster processing

## Contributing

Contributions are welcome! Please feel free to submit pull requests or open issues for bugs and feature requests.

### Development Setup

```bash
# Clone for development
git clone <repository-url>
cd FaceSwap

# Install in development mode
pip install -e .

# Install development dependencies
pip install pytest black flake8
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- **Dlib**: Davis King's machine learning library
- **OpenCV**: Open Source Computer Vision Library
- **Qt/PySide**: Cross-platform GUI toolkit

## Disclaimer

This tool is for educational and creative purposes. Please use responsibly and ensure you have permission to use any faces or videos you process. Be mindful of privacy and consent when creating face-swapped content.