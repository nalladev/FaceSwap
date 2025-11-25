#!/usr/bin/env python3
"""
FaceSwap - Local Face Swapping Tool
Main application entry point.
"""

import sys
import os
import logging
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon

# Add project root to Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from gui.main_window import MainWindow

# Configure logging
def setup_logging():
    """Set up logging configuration."""
    log_format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # Create logs directory
    logs_dir = project_root / "logs"
    logs_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format=log_format,
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler(logs_dir / 'faceswap.log')
        ]
    )

logger = logging.getLogger(__name__)

def check_requirements():
    """Check if all required dependencies and files are available."""
    try:
        # Check Python version
        if sys.version_info < (3, 8):
            return False, "Python 3.8 or higher is required"

        # Check required packages
        required_packages = ['cv2', 'dlib', 'numpy', 'PySide6']
        missing_packages = []
        
        for package in required_packages:
            try:
                __import__(package)
            except ImportError:
                missing_packages.append(package)

        if missing_packages:
            pip_names = {
                'cv2': 'opencv-python',
                'PySide6': 'PySide6'
            }
            missing_pip = [pip_names.get(pkg, pkg) for pkg in missing_packages]
            return False, f"Missing packages: {', '.join(missing_pip)}\n" \
                         f"Install with: pip install {' '.join(missing_pip)}"

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
            return False, f"Missing model files in {models_dir}:\n" \
                         f"{', '.join(missing_models)}\n\n" \
                         f"Run: python download_models.py"

        return True, "All requirements satisfied"

    except Exception as e:
        return False, f"Error checking requirements: {str(e)}"

def create_application():
    """Create and configure the QApplication."""
    app = QApplication(sys.argv)

    # Set application properties
    app.setApplicationName("FaceSwap")
    app.setApplicationDisplayName("FaceSwap - Local Face Swapping Tool")
    app.setApplicationVersion("1.0.1")
    app.setOrganizationName("FaceSwap")

    # Set application icon if available
    icon_path = project_root / "assets" / "icon.png"
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))

    return app

def show_error_dialog(title: str, message: str):
    """Show an error dialog."""
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

        logger.info("Application ready")

        # Run application event loop
        exit_code = app.exec()
        logger.info(f"Application exiting with code: {exit_code}")
        return exit_code

    except ImportError as e:
        error_msg = f"Import error: {str(e)}\n\nInstall requirements:\npip install -r requirements.txt"
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
    exit_code = main()
    sys.exit(exit_code)
