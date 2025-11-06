#!/usr/bin/env python3
"""
FaceSwap - Local Face Swapping Tool
Main application entry point.

This is the main entry point for the FaceSwap application. It initializes the
PySide6 GUI application and launches the main window.

Usage:
    python main.py

Requirements:
    - Python 3.8+
    - PySide6
    - OpenCV
    - Dlib
    - NumPy
    - Required Dlib model files in models/ directory
"""

import sys
import os
import logging
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt, QDir
from PySide6.QtGui import QIcon, QPixmap

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from gui.main_window import MainWindow

# Configure logging
def setup_logging():
    """Set up logging configuration."""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('faceswap.log')
        ]
    )

def check_requirements():
    """
    Check if all required dependencies and files are available.
    
    Returns:
        tuple: (success: bool, error_message: str)
    """
    try:
        # Check Python version
        if sys.version_info < (3, 8):
            return False, "Python 3.8 or higher is required"
        
        # Check required packages
        required_packages = [
            ('cv2', 'opencv-python'),
            ('dlib', 'dlib'),
            ('numpy', 'numpy'),
            ('PySide6', 'PySide6')
        ]
        
        missing_packages = []
        for package, pip_name in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(pip_name)
        
        if missing_packages:
            return False, f"Missing required packages: {', '.join(missing_packages)}\n" \
                         f"Install with: pip install {' '.join(missing_packages)}"
        
        # Check for required model files
        models_dir = project_root / "models"
        required_models = [
            "shape_predictor_68_face_landmarks.dat",
            "dlib_face_recognition_resnet_model_v1.dat"
        ]
        
        missing_models = []
        for model_file in required_models:
            model_path = models_dir / model_file
            if not model_path.exists():
                missing_models.append(model_file)
        
        if missing_models:
            model_urls = {
                "shape_predictor_68_face_landmarks.dat": 
                    "http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2",
                "dlib_face_recognition_resnet_model_v1.dat": 
                    "http://dlib.net/files/dlib_face_recognition_resnet_model_v1.dat.bz2"
            }
            
            error_msg = f"Missing required model files in {models_dir}:\n\n"
            for model in missing_models:
                error_msg += f"• {model}\n"
                if model in model_urls:
                    error_msg += f"  Download: {model_urls[model]}\n"
            
            error_msg += f"\nCreate the models directory and download the required files:\n"
            error_msg += f"mkdir -p {models_dir}\n"
            error_msg += f"# Download and extract the .dat files to the models directory"
            
            return False, error_msg
        
        return True, "All requirements satisfied"
        
    except Exception as e:
        return False, f"Error checking requirements: {str(e)}"

def create_application():
    """
    Create and configure the QApplication.
    
    Returns:
        QApplication: Configured application instance
    """
    # Set application attributes before creating QApplication
    # High DPI scaling is enabled by default in Qt 6, so these attributes are deprecated
    # QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)  # Deprecated in Qt 6
    # QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)     # Deprecated in Qt 6
    
    # Force native file dialogs (PopOS system dialogs)
    # Note: By default, Qt uses native dialogs, but we ensure it's not disabled
    pass  # Native dialogs should be used by default
    
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("FaceSwap")
    app.setApplicationDisplayName("FaceSwap - Local Face Swapping Tool")
    app.setApplicationVersion("1.0.0")
    app.setOrganizationName("FaceSwap")
    app.setOrganizationDomain("faceswap.local")
    
    # Set application icon if available
    icon_path = project_root / "assets" / "icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    # Set application style
    app.setStyle("Fusion")  # Modern cross-platform style
    
    return app

def show_error_dialog(title: str, message: str):
    """
    Show an error dialog without creating a full application.
    
    Args:
        title: Dialog title
        message: Error message to display
    """
    app = QApplication(sys.argv)
    
    msg_box = QMessageBox()
    msg_box.setIcon(QMessageBox.Critical)
    msg_box.setWindowTitle(title)
    msg_box.setText(title)
    msg_box.setDetailedText(message)
    msg_box.setStandardButtons(QMessageBox.Ok)
    
    msg_box.exec()

def main():
    """Main application entry point."""
    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting FaceSwap application...")
    logger.info(f"Python version: {sys.version}")
    logger.info(f"Project root: {project_root}")
    
    try:
        # Check requirements
        requirements_ok, requirements_message = check_requirements()
        if not requirements_ok:
            logger.error(f"Requirements check failed: {requirements_message}")
            show_error_dialog("Requirements Error", requirements_message)
            return 1
        
        logger.info("Requirements check passed")
        
        # Create application
        app = create_application()
        logger.info("QApplication created successfully")
        
        # Create and show main window
        main_window = MainWindow()
        main_window.show()
        
        logger.info("Main window created and shown")
        logger.info("Application ready - waiting for user interaction")
        
        # Run application event loop
        exit_code = app.exec()
        
        logger.info(f"Application exiting with code: {exit_code}")
        return exit_code
        
    except ImportError as e:
        error_msg = f"Import error: {str(e)}\n\nPlease ensure all required packages are installed:\n" \
                   f"pip install -r requirements.txt"
        logger.error(error_msg)
        show_error_dialog("Import Error", error_msg)
        return 1
        
    except Exception as e:
        error_msg = f"Unexpected error: {str(e)}"
        logger.error(error_msg, exc_info=True)
        show_error_dialog("Application Error", error_msg)
        return 1

if __name__ == "__main__":
    # Ensure we're running from the correct directory
    os.chdir(project_root)
    
    # Run the application
    exit_code = main()
    sys.exit(exit_code)