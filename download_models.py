#!/usr/bin/env python3
"""
Model Download Script for FaceSwap Application

This script downloads the required Dlib model files needed for face detection,
landmark prediction, and face recognition. The models are downloaded from the
official Dlib repository and extracted to the models directory.

Usage:
    python download_models.py

The script will:
1. Create the models directory if it doesn't exist
2. Download the compressed model files
3. Extract them to .dat files
4. Verify the downloads
5. Clean up temporary files
"""

import os
import sys
import urllib.request
import urllib.error
import bz2
import shutil
from pathlib import Path
import hashlib
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

# Model configuration
MODELS = {
    "shape_predictor_68_face_landmarks.dat": {
        # Updated URL - original may be unreliable
        "url": "https://github.com/davisking/dlib-models/raw/master/shape_predictor_68_face_landmarks.dat.bz2",
        "fallback_url": "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2",
        "compressed_file": "shape_predictor_68_face_landmarks.dat.bz2",
        "description": "68-point facial landmark predictor",
        "size_mb": 99.7,
        # SHA256 hash of the uncompressed .dat file (if known)
        "sha256": None
    },
    "dlib_face_recognition_resnet_model_v1.dat": {
        "url": "https://github.com/davisking/dlib-models/raw/master/dlib_face_recognition_resnet_model_v1.dat.bz2",
        "fallback_url": "http://dlib.net/files/dlib_face_recognition_resnet_model_v1.dat.bz2",
        "compressed_file": "dlib_face_recognition_resnet_model_v1.dat.bz2", 
        "description": "Face recognition ResNet model",
        "size_mb": 22.5,
        "sha256": None
    }
}

def create_models_directory():
    """Create the models directory if it doesn't exist."""
    models_dir = Path("models")
    models_dir.mkdir(exist_ok=True)
    logger.info(f"Models directory: {models_dir.absolute()}")
    return models_dir

def download_file_with_progress(url, filename, fallback_url=None):
    """
    Download a file with progress reporting and fallback URL.
    
    Args:
        url: Primary URL to download from
        filename: Local filename to save to
        fallback_url: Fallback URL if primary fails
        
    Returns:
        bool: True if successful, False otherwise
    """
    urls_to_try = [url]
    if fallback_url:
        urls_to_try.append(fallback_url)
    
    for attempt_url in urls_to_try:
        try:
            logger.info(f"Downloading {filename} from {attempt_url}...")
            
            def progress_hook(block_num, block_size, total_size):
                """Progress reporting hook."""
                if total_size > 0:
                    percent = min(100, (block_num * block_size * 100) // total_size)
                    size_mb = total_size / (1024 * 1024)
                    downloaded_mb = (block_num * block_size) / (1024 * 1024)
                    print(f"\rProgress: {percent:3d}% ({downloaded_mb:.1f}/{size_mb:.1f} MB)", end="", flush=True)
            
            urllib.request.urlretrieve(attempt_url, filename, progress_hook)
            print()  # New line after progress
            logger.info(f"Downloaded: {filename}")
            return True
            
        except urllib.error.URLError as e:
            logger.warning(f"Failed to download from {attempt_url}: {e}")
            if attempt_url == urls_to_try[-1]:  # Last URL failed
                logger.error(f"All download attempts failed for {filename}")
                return False
            continue
        except Exception as e:
            logger.warning(f"Unexpected error downloading from {attempt_url}: {e}")
            continue
    
    return False

def extract_bz2_file(compressed_file, output_file):
    """
    Extract a bz2 compressed file.
    
    Args:
        compressed_file: Path to compressed file
        output_file: Path for extracted file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        logger.info(f"Extracting {compressed_file}...")
        
        with bz2.BZ2File(compressed_file, 'rb') as f_in:
            with open(output_file, 'wb') as f_out:
                # Copy data in chunks to show progress for large files
                chunk_size = 1024 * 1024  # 1MB chunks
                total_size = os.path.getsize(compressed_file)
                processed = 0
                
                while True:
                    chunk = f_in.read(chunk_size)
                    if not chunk:
                        break
                    f_out.write(chunk)
                    processed += len(chunk)
                    
                    # Show progress (approximate since we're reading compressed data)
                    if total_size > 0:
                        percent = min(100, (processed * 100) // total_size)
                        print(f"\rExtracting: {percent:3d}%", end="", flush=True)
        
        print()  # New line after progress
        logger.info(f"Extracted: {output_file}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to extract {compressed_file}: {e}")
        return False

def verify_file(file_path, expected_sha256=None):
    """
    Verify a downloaded file.
    
    Args:
        file_path: Path to file to verify
        expected_sha256: Expected SHA256 hash (optional)
        
    Returns:
        bool: True if valid, False otherwise
    """
    if not os.path.exists(file_path):
        logger.error(f"File not found: {file_path}")
        return False
    
    file_size = os.path.getsize(file_path)
    if file_size == 0:
        logger.error(f"File is empty: {file_path}")
        return False
    
    logger.info(f"File size: {file_size / (1024*1024):.1f} MB")
    
    # Verify SHA256 hash if provided
    if expected_sha256:
        logger.info("Verifying file integrity...")
        sha256_hash = hashlib.sha256()
        
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                sha256_hash.update(chunk)
        
        calculated_hash = sha256_hash.hexdigest()
        if calculated_hash.lower() == expected_sha256.lower():
            logger.info("File integrity verified ✓")
            return True
        else:
            logger.error(f"File integrity check failed!")
            logger.error(f"Expected: {expected_sha256}")
            logger.error(f"Got:      {calculated_hash}")
            return False
    
    logger.info("File appears valid ✓")
    return True

def cleanup_temp_files(temp_files):
    """Remove temporary files."""
    for temp_file in temp_files:
        try:
            if os.path.exists(temp_file):
                os.remove(temp_file)
                logger.info(f"Removed temporary file: {temp_file}")
        except Exception as e:
            logger.warning(f"Could not remove {temp_file}: {e}")

def download_all_models():
    """Download and extract all required model files."""
    # Create models directory
    models_dir = create_models_directory()
    
    success_count = 0
    temp_files = []
    
    logger.info(f"Starting download of {len(MODELS)} model files...")
    logger.info("This may take several minutes depending on your internet connection.")
    
    for model_file, config in MODELS.items():
        logger.info(f"\n{'='*60}")
        logger.info(f"Processing: {config['description']}")
        logger.info(f"Model file: {model_file}")
        logger.info(f"Expected size: ~{config['size_mb']} MB")
        
        model_path = models_dir / model_file
        compressed_path = models_dir / config['compressed_file']
        
        # Check if model already exists
        if model_path.exists():
            if verify_file(model_path, config['sha256']):
                logger.info(f"Model already exists and is valid: {model_file}")
                success_count += 1
                continue
            else:
                logger.warning(f"Existing model file is invalid, re-downloading...")
                try:
                    os.remove(model_path)
                except:
                    pass
        
        # Download compressed file
        fallback_url = config.get('fallback_url')
        if not download_file_with_progress(config['url'], compressed_path, fallback_url):
            logger.error(f"Failed to download {model_file}")
            continue
        
        temp_files.append(compressed_path)
        
        # Extract the file
        if not extract_bz2_file(compressed_path, model_path):
            logger.error(f"Failed to extract {model_file}")
            continue
        
        # Verify the extracted file
        if not verify_file(model_path, config['sha256']):
            logger.error(f"Failed to verify {model_file}")
            continue
        
        success_count += 1
        logger.info(f"Successfully installed: {model_file} ✓")
    
    # Clean up temporary files
    logger.info(f"\n{'='*60}")
    logger.info("Cleaning up temporary files...")
    cleanup_temp_files(temp_files)
    
    # Summary
    logger.info(f"\n{'='*60}")
    logger.info("DOWNLOAD SUMMARY")
    logger.info(f"Successfully downloaded: {success_count}/{len(MODELS)} models")
    
    if success_count == len(MODELS):
        logger.info("✓ All models downloaded successfully!")
        logger.info("You can now run the FaceSwap application.")
        return True
    else:
        failed_count = len(MODELS) - success_count
        logger.error(f"✗ {failed_count} model(s) failed to download.")
        logger.error("Please check your internet connection and try again.")
        return False

def check_existing_models():
    """
    Check which models are already downloaded.
    
    Returns:
        dict: Status of each model file
    """
    models_dir = Path("models")
    if not models_dir.exists():
        return {}
    
    status = {}
    for model_file, config in MODELS.items():
        model_path = models_dir / model_file
        if model_path.exists():
            if verify_file(model_path, config['sha256']):
                status[model_file] = "valid"
            else:
                status[model_file] = "invalid"
        else:
            status[model_file] = "missing"
    
    return status

def main():
    """Main function."""
    print("FaceSwap Model Downloader")
    print("=" * 40)
    
    # Check Python version
    if sys.version_info < (3, 6):
        logger.error("Python 3.6 or higher is required")
        return 1
    
    # Check existing models
    logger.info("Checking existing models...")
    existing_status = check_existing_models()
    
    if existing_status:
        logger.info("Current model status:")
        for model_file, status in existing_status.items():
            status_symbol = {"valid": "✓", "invalid": "✗", "missing": "◯"}[status]
            logger.info(f"  {status_symbol} {model_file}: {status}")
    
    # Ask user if they want to proceed
    if existing_status and all(status == "valid" for status in existing_status.values()):
        logger.info("\nAll models are already downloaded and valid!")
        response = input("Do you want to re-download anyway? (y/N): ").strip().lower()
        if response not in ['y', 'yes']:
            logger.info("Skipping download.")
            return 0
    
    # Download models
    if download_all_models():
        logger.info("\n🎉 Setup complete! You can now use FaceSwap.")
        return 0
    else:
        logger.error("\n❌ Setup failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        logger.info("\nDownload cancelled by user.")
        sys.exit(1)
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        sys.exit(1)