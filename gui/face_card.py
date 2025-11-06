import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFileDialog, QFrame, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QFont
import cv2
import numpy as np
import os
import logging

logger = logging.getLogger(__name__)

class FaceCard(QWidget):
    """
    Widget representing a detected face with options to assign a swap image.
    Displays the detected face thumbnail and provides interface to select replacement image.
    """
    
    # Signal emitted when a swap image is selected
    swap_image_selected = Signal(int, str)  # face_index, image_path
    
    def __init__(self, face_index: int, face_data: dict, parent=None):
        """
        Initialize face card widget.
        
        Args:
            face_index: Index of this face in the unique faces list
            face_data: Dictionary containing face image and metadata
            parent: Parent widget
        """
        super().__init__(parent)
        self.face_index = face_index
        self.face_data = face_data
        self.swap_image_path = None
        
        self.setup_ui()
        self.load_face_image()
    
    def setup_ui(self):
        """Set up the user interface for the face card."""
        # Set up the main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(8)
        
        # Create frame for styling
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel | QFrame.Raised)
        frame.setLineWidth(2)
        frame_layout = QVBoxLayout(frame)
        frame_layout.setContentsMargins(8, 8, 8, 8)
        frame_layout.setSpacing(6)
        
        # Face index label
        index_label = QLabel(f"Face #{self.face_index + 1}")
        index_label.setAlignment(Qt.AlignCenter)
        font = QFont()
        font.setBold(True)
        font.setPointSize(12)
        index_label.setFont(font)
        frame_layout.addWidget(index_label)
        
        # Face image display
        self.face_label = QLabel()
        self.face_label.setAlignment(Qt.AlignCenter)
        self.face_label.setMinimumSize(150, 150)
        self.face_label.setMaximumSize(200, 200)
        self.face_label.setScaledContents(True)
        self.face_label.setStyleSheet("""
            QLabel {
                border: 2px solid #cccccc;
                border-radius: 8px;
                background-color: #f0f0f0;
            }
        """)
        frame_layout.addWidget(self.face_label)
        
        # Swap image info
        self.swap_info_label = QLabel("Swap with: None")
        self.swap_info_label.setAlignment(Qt.AlignCenter)
        self.swap_info_label.setWordWrap(True)
        self.swap_info_label.setStyleSheet("color: #666666; font-size: 10px;")
        frame_layout.addWidget(self.swap_info_label)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.setSpacing(4)
        
        # Select image button
        self.select_button = QPushButton("Select Image...")
        self.select_button.clicked.connect(self.select_swap_image)
        self.select_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        button_layout.addWidget(self.select_button)
        
        # Clear button
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_swap_image)
        self.clear_button.setEnabled(False)
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
            QPushButton:pressed {
                background-color: #c5150a;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        button_layout.addWidget(self.clear_button)
        
        frame_layout.addLayout(button_layout)
        
        # Add frame to main layout
        layout.addWidget(frame)
        
        # Set size policy
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setFixedSize(220, 300)
    
    def load_face_image(self):
        """Load and display the detected face image."""
        try:
            face_image = self.face_data['image']
            
            # Convert from RGB to BGR for Qt
            if len(face_image.shape) == 3:
                face_image_bgr = cv2.cvtColor(face_image, cv2.COLOR_RGB2BGR)
            else:
                face_image_bgr = face_image
            
            # Convert to Qt format
            height, width = face_image_bgr.shape[:2]
            bytes_per_line = 3 * width if len(face_image_bgr.shape) == 3 else width
            
            if len(face_image_bgr.shape) == 3:
                # Color image
                q_image = QPixmap.fromImage(
                    face_image_bgr.data, width, height, bytes_per_line
                ).scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            else:
                # Grayscale image
                q_image = QPixmap.fromImage(
                    face_image_bgr.data, width, height, bytes_per_line
                ).scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
            
            # Alternative method using OpenCV to encode image
            success, buffer = cv2.imencode('.jpg', face_image_bgr)
            if success:
                pixmap = QPixmap()
                pixmap.loadFromData(buffer.tobytes())
                scaled_pixmap = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                self.face_label.setPixmap(scaled_pixmap)
            else:
                self.face_label.setText("Failed to load face image")
                
        except Exception as e:
            logger.error(f"Error loading face image for face {self.face_index}: {e}")
            self.face_label.setText("Error loading image")
    
    def select_swap_image(self):
        """Open file dialog to select swap image."""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Select Swap Image")
        file_dialog.setNameFilter("Image Files (*.jpg *.jpeg *.png *.bmp *.tiff *.tif)")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                image_path = selected_files[0]
                self.set_swap_image(image_path)
    
    def set_swap_image(self, image_path: str):
        """
        Set the swap image for this face.
        
        Args:
            image_path: Path to the swap image file
        """
        try:
            # Validate that the image can be loaded
            test_image = cv2.imread(image_path)
            if test_image is None:
                raise ValueError(f"Could not load image: {image_path}")
            
            self.swap_image_path = image_path
            
            # Update UI
            filename = os.path.basename(image_path)
            if len(filename) > 25:
                filename = filename[:22] + "..."
            
            self.swap_info_label.setText(f"Swap with: {filename}")
            self.swap_info_label.setStyleSheet("color: #2e7d32; font-size: 10px; font-weight: bold;")
            self.clear_button.setEnabled(True)
            
            # Update button appearance
            self.select_button.setText("Change Image...")
            self.select_button.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
                QPushButton:pressed {
                    background-color: #1565C0;
                }
            """)
            
            # Emit signal
            self.swap_image_selected.emit(self.face_index, image_path)
            
            logger.info(f"Swap image set for face {self.face_index}: {filename}")
            
        except Exception as e:
            logger.error(f"Error setting swap image: {e}")
            # Show error message could be added here
    
    def clear_swap_image(self):
        """Clear the assigned swap image."""
        self.swap_image_path = None
        
        # Update UI
        self.swap_info_label.setText("Swap with: None")
        self.swap_info_label.setStyleSheet("color: #666666; font-size: 10px;")
        self.clear_button.setEnabled(False)
        
        # Reset button appearance
        self.select_button.setText("Select Image...")
        self.select_button.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        
        # Emit signal with empty path
        self.swap_image_selected.emit(self.face_index, "")
        
        logger.info(f"Swap image cleared for face {self.face_index}")
    
    def get_swap_image_path(self) -> str:
        """
        Get the path to the assigned swap image.
        
        Returns:
            Path to swap image, or empty string if none assigned
        """
        return self.swap_image_path if self.swap_image_path else ""
    
    def has_swap_image(self) -> bool:
        """
        Check if this face has a swap image assigned.
        
        Returns:
            True if swap image is assigned, False otherwise
        """
        return self.swap_image_path is not None and self.swap_image_path != ""
    
    def update_face_data(self, face_data: dict):
        """
        Update the face data and refresh the display.
        
        Args:
            face_data: Updated face data dictionary
        """
        self.face_data = face_data
        self.load_face_image()