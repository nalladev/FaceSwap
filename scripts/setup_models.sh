#!/bin/bash

# Setup script for downloading required model files

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
MODELS_DIR="$PROJECT_DIR/models"

echo "Setting up model files for FaceSwap..."

# Create models directory if it doesn't exist
mkdir -p "$MODELS_DIR"

# Download shape predictor model if it doesn't exist
if [ ! -f "$MODELS_DIR/shape_predictor_68_face_landmarks.dat" ]; then
    echo "Downloading shape predictor model..."
    cd "$MODELS_DIR"
    
    # Download the compressed model
    if [ ! -f "shape_predictor_68_face_landmarks.dat.bz2" ]; then
        wget -O shape_predictor_68_face_landmarks.dat.bz2 \
            http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
    fi
    
    # Extract the model
    if [ -f "shape_predictor_68_face_landmarks.dat.bz2" ]; then
        bzip2 -d shape_predictor_68_face_landmarks.dat.bz2
        echo "Model extracted successfully!"
    else
        echo "Failed to download model file"
        exit 1
    fi
else
    echo "Shape predictor model already exists"
fi

echo "Model setup complete!"
