import sys
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QFileDialog, QFrame, QSizePolicy)
from PySide6.QtCore import Qt, Signal, QSize
from PySide6.QtGui import QPixmap, QFont, QPainter, QBrush, QPen
import cv2
import numpy as np
import os
import logging

logger = logging.getLogger(__name__)

class CircleImageLabel(QLabel):
    """Custom label that displays images in a circle."""
    
    def __init__(self, size=80):
        super().__init__()
        self.circle_size = size
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignCenter)
        self.setStyleSheet(f"""
            QLabel {{
                border: 2px solid #bdc3c7;
                border-radius: {size//2}px;
                background-color: #ecf0f1;
            }}
        """)
        self.original_pixmap = None
    
    def setCirclePixmap(self, pixmap):
        """Set pixmap and make it circular."""
        if pixmap and not pixmap.isNull():
            self.original_pixmap = pixmap
            # Scale pixmap to fit circle
            scaled = pixmap.scaled(
                self.circle_size - 4, self.circle_size - 4, 
                Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
            
            # Create circular mask
            circular_pixmap = QPixmap(self.circle_size - 4, self.circle_size - 4)
            circular_pixmap.fill(Qt.transparent)
            
            painter = QPainter(circular_pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Create circular path
            painter.setBrush(QBrush(scaled))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(0, 0, self.circle_size - 4, self.circle_size - 4)
            
            painter.end()
            self.setPixmap(circular_pixmap)
        else:
            self.clear()

class SwapCircleLabel(QLabel):
    """Circle label that can show either a plus symbol or an image."""
    
    clicked = Signal()
    
    def __init__(self, size=80):
        super().__init__()
        self.circle_size = size
        self.setFixedSize(size, size)
        self.setAlignment(Qt.AlignCenter)
        self.has_image = False
        self.original_pixmap = None
        self.setCursor(Qt.PointingHandCursor)
        self.reset_to_plus()
    
    def reset_to_plus(self):
        """Reset to plus state."""
        self.has_image = False
        self.original_pixmap = None
        self.clear()
        self.setText("+")
        self.setStyleSheet(f"""
            QLabel {{
                border: 2px dashed #95a5a6;
                border-radius: {self.circle_size//2}px;
                background-color: #f8f9fa;
                color: #7f8c8d;
                font-size: 24px;
                font-weight: bold;
            }}
            QLabel:hover {{
                border-color: #3498db;
                background-color: #e3f2fd;
                color: #2196f3;
            }}
        """)
    
    def setCirclePixmap(self, pixmap):
        """Set pixmap and make it circular."""
        if pixmap and not pixmap.isNull():
            self.has_image = True
            self.original_pixmap = pixmap
            self.setText("")  # Clear the "+" text
            
            # Scale pixmap to fit circle
            scaled = pixmap.scaled(
                self.circle_size - 4, self.circle_size - 4, 
                Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation
            )
            
            # Create circular mask
            circular_pixmap = QPixmap(self.circle_size - 4, self.circle_size - 4)
            circular_pixmap.fill(Qt.transparent)
            
            painter = QPainter(circular_pixmap)
            painter.setRenderHint(QPainter.Antialiasing)
            
            # Create circular path
            painter.setBrush(QBrush(scaled))
            painter.setPen(Qt.NoPen)
            painter.drawEllipse(0, 0, self.circle_size - 4, self.circle_size - 4)
            
            painter.end()
            self.setPixmap(circular_pixmap)
            
            # Update styling for image state
            self.setStyleSheet(f"""
                QLabel {{
                    border: 2px solid #27ae60;
                    border-radius: {self.circle_size//2}px;
                    background-color: #ecf0f1;
                }}
                QLabel:hover {{
                    border-color: #229954;
                }}
            """)
        else:
            self.reset_to_plus()
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

class FaceCard(QWidget):
    """Widget displaying a face detection result with swap image selection."""
    
    swap_image_selected = Signal(int, str)  # face_index, image_path
    
    def __init__(self, face_index: int, face_data: dict, parent=None):
        super().__init__(parent)
        self.face_index = face_index
        self.face_data = face_data
        self.swap_image_path = None
        self.setup_ui()
        self.load_face_image()
    
    def setup_ui(self):
        """Set up the user interface with paired circles layout."""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Face title
        title_label = QLabel(f"Face #{self.face_index + 1}")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setFont(QFont("Arial", 10, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 5px;")
        layout.addWidget(title_label)
        
        # Circles container
        circles_layout = QHBoxLayout()
        circles_layout.setSpacing(20)
        circles_layout.setContentsMargins(5, 0, 5, 0)
        
        # Original face circle
        face_container = QVBoxLayout()
        face_container.setSpacing(3)
        
        self.face_circle = CircleImageLabel(80)
        self.face_circle.setMinimumSize(84, 84)  # Ensure minimum size
        face_container.addWidget(self.face_circle, alignment=Qt.AlignCenter)
        
        face_label = QLabel("Detected")
        face_label.setAlignment(Qt.AlignCenter)
        face_label.setStyleSheet("color: #7f8c8d; font-size: 9px;")
        face_container.addWidget(face_label)
        
        circles_layout.addLayout(face_container)
        
        # Arrow or connector
        arrow_label = QLabel("→")
        arrow_label.setAlignment(Qt.AlignCenter)
        arrow_label.setStyleSheet("color: #95a5a6; font-size: 16px; font-weight: bold;")
        arrow_label.setFixedWidth(15)
        circles_layout.addWidget(arrow_label)
        
        # Swap image circle
        swap_container = QVBoxLayout()
        swap_container.setSpacing(3)
        
        self.swap_circle = SwapCircleLabel(80)
        self.swap_circle.clicked.connect(self.select_swap_image)
        self.swap_circle.setMinimumSize(84, 84)  # Ensure minimum size
        swap_container.addWidget(self.swap_circle, alignment=Qt.AlignCenter)
        
        self.swap_label = QLabel("Add Swap")
        self.swap_label.setAlignment(Qt.AlignCenter)
        self.swap_label.setStyleSheet("color: #7f8c8d; font-size: 9px;")
        swap_container.addWidget(self.swap_label)
        
        circles_layout.addLayout(swap_container)
        
        layout.addLayout(circles_layout)
        
        # Clear button (hidden initially)
        self.clear_button = QPushButton("Clear")
        self.clear_button.clicked.connect(self.clear_swap_image)
        self.clear_button.setVisible(False)
        self.clear_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 4px 12px;
                border-radius: 3px;
                font-size: 9px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        layout.addWidget(self.clear_button, alignment=Qt.AlignCenter)
        
        # Set fixed size for the card with more width for both circles
        self.setFixedSize(240, 150)
        self.setMinimumSize(240, 150)
        
        # Card styling
        self.setStyleSheet("""
            FaceCard {
                background-color: white;
                border: 1px solid #ddd;
                border-radius: 8px;
            }
            FaceCard:hover {
                border-color: #3498db;
            }
        """)
    
    def load_face_image(self):
        """Load and display the detected face image in the circle."""
        try:
            face_image = self.face_data['image']
            
            # Debug information
            logger.debug(f"Loading face image {self.face_index}: shape={face_image.shape}, dtype={face_image.dtype}")
            
            # Ensure image is in the correct format
            if len(face_image.shape) == 3 and face_image.shape[2] == 3:
                # Image is already in BGR format from OpenCV
                face_image_bgr = face_image.copy()
            elif len(face_image.shape) == 3 and face_image.shape[2] == 4:
                # Convert RGBA to BGR
                face_image_bgr = cv2.cvtColor(face_image, cv2.COLOR_RGBA2BGR)
            else:
                # Grayscale - convert to BGR
                face_image_bgr = cv2.cvtColor(face_image, cv2.COLOR_GRAY2BGR)
            
            # Ensure the image data is in the correct range
            if face_image_bgr.dtype != np.uint8:
                if face_image_bgr.max() <= 1.0:
                    face_image_bgr = (face_image_bgr * 255).astype(np.uint8)
                else:
                    face_image_bgr = face_image_bgr.astype(np.uint8)
            
            # Use OpenCV to encode image to JPEG format
            success, buffer = cv2.imencode('.jpg', face_image_bgr)
            if success:
                # Load pixmap from encoded data
                pixmap = QPixmap()
                if pixmap.loadFromData(buffer.tobytes()):
                    self.face_circle.setCirclePixmap(pixmap)
                    logger.debug(f"Successfully loaded face image for face {self.face_index}")
                else:
                    logger.error(f"Failed to decode image data for face {self.face_index}")
            else:
                logger.error(f"Failed to encode image for face {self.face_index}")
                
        except Exception as e:
            logger.error(f"Error loading face image for face {self.face_index}: {e}")
            import traceback
            logger.error(f"Traceback: {traceback.format_exc()}")
    
    def select_swap_image(self):
        """Open file dialog to select swap image."""
        image_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Swap Image",
            "",
            "Image Files (*.jpg *.jpeg *.png *.bmp *.tiff *.tif);;All Files (*)"
        )
        
        if image_path:
            self.set_swap_image(image_path)
    
    def set_swap_image(self, image_path: str):
        """Set the swap image for this face."""
        try:
            if not os.path.exists(image_path):
                logger.error(f"Swap image file not found: {image_path}")
                return
            
            # Load and display the swap image
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                self.swap_circle.setCirclePixmap(pixmap)
                
                self.swap_image_path = image_path
                self.swap_label.setText("Ready")
                self.swap_label.setStyleSheet("color: #27ae60; font-size: 9px; font-weight: bold;")
                self.clear_button.setVisible(True)
                
                # Emit signal
                self.swap_image_selected.emit(self.face_index, image_path)
                
                logger.info(f"Swap image set for face {self.face_index}: {os.path.basename(image_path)}")
            else:
                logger.error(f"Failed to load swap image: {image_path}")
                
        except Exception as e:
            logger.error(f"Error setting swap image for face {self.face_index}: {e}")
    
    def clear_swap_image(self):
        """Clear the swap image."""
        # Reset swap circle to plus symbol
        self.swap_circle.reset_to_plus()
        
        self.swap_image_path = None
        self.swap_label.setText("Add Swap")
        self.swap_label.setStyleSheet("color: #7f8c8d; font-size: 9px;")
        self.clear_button.setVisible(False)
        
        # Emit signal with empty path
        self.swap_image_selected.emit(self.face_index, "")
        
        logger.info(f"Swap image cleared for face {self.face_index}")
    
    def has_swap_image(self) -> bool:
        """Check if this face has a swap image assigned."""
        return self.swap_image_path is not None and os.path.exists(self.swap_image_path)
    
    def get_swap_image_path(self) -> str:
        """Get the path to the swap image."""
        return self.swap_image_path if self.swap_image_path else ""