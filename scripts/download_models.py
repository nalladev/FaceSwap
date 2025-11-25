#!/usr/bin/env python3
"""
Download required model files for FaceSwap application.
"""

import os
import requests
import bz2
import shutil
from pathlib import Path

def download_file(url, destination):
    """Download a file from URL to destination."""
    print(f"Downloading {url} to {destination}")
    response = requests.get(url, stream=True)
    response.raise_for_status()
    
    with open(destination, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"Downloaded {destination}")

def extract_bz2(source, destination):
    """Extract a bz2 file."""
    print(f"Extracting {source} to {destination}")
    with bz2.open(source, 'rb') as src, open(destination, 'wb') as dst:
        shutil.copyfileobj(src, dst)
    print(f"Extracted {destination}")

def main():
    """Download and extract model files."""
    # Create models directory
    models_dir = Path(__file__).parent.parent / "models"
    models_dir.mkdir(exist_ok=True)
    
    # Download shape predictor model
    shape_predictor_url = "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2"
    shape_predictor_bz2 = models_dir / "shape_predictor_68_face_landmarks.dat.bz2"
    shape_predictor_dat = models_dir / "shape_predictor_68_face_landmarks.dat"
    
    if not shape_predictor_dat.exists():
        if not shape_predictor_bz2.exists():
            try:
                download_file(shape_predictor_url, shape_predictor_bz2)
            except Exception as e:
                print(f"Failed to download model: {e}")
                print("Please manually download the file and place it in the models directory")
                return False
        
        try:
            extract_bz2(shape_predictor_bz2, shape_predictor_dat)
            shape_predictor_bz2.unlink()  # Remove compressed file
        except Exception as e:
            print(f"Failed to extract model: {e}")
            return False
    else:
        print(f"Model file already exists: {shape_predictor_dat}")
    
    print("Model download complete!")
    return True

if __name__ == "__main__":
    main()
