#!/bin/bash

# Setup script for downloading required model files

set -e

echo "Setting up model files for FaceSwap..."

# Create models directory if it doesn't exist
mkdir -p models

# Download shape predictor model if it doesn't exist
if [ ! -f "models/shape_predictor_68_face_landmarks.dat" ]; then
    echo "Downloading shape predictor model..."
    cd models
    
    # Download the compressed model
    if [ ! -f "shape_predictor_68_face_landmarks.dat.bz2" ]; then
        echo "Downloading from dlib.net..."
        wget -O shape_predictor_68_face_landmarks.dat.bz2 \
            http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
    fi
    
    # Extract the model
    if [ -f "shape_predictor_68_face_landmarks.dat.bz2" ]; then
        echo "Extracting model file..."
        bzip2 -d shape_predictor_68_face_landmarks.dat.bz2
        echo "Model extracted successfully!"
    else
        echo "Failed to download model file"
        exit 1
    fi
    
    cd ..
else
    echo "Shape predictor model already exists"
fi

echo "Model setup complete!"
echo "File size: $(ls -lh models/shape_predictor_68_face_landmarks.dat 2>/dev/null || echo 'File not found')"
