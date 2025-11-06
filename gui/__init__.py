"""
GUI package for FaceSwap application.

This package contains all the GUI components built with PySide6:
- Main application window
- Face card widgets for displaying detected faces
- Progress dialogs for long-running operations
- Utility widgets and dialogs
"""

from .main_window import MainWindow
from .face_card import FaceCard
from .progress_dialog import ProgressDialog

__all__ = ['MainWindow', 'FaceCard', 'ProgressDialog']