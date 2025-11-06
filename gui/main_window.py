import sys
import os
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QPushButton, QFileDialog, QScrollArea, 
                               QGridLayout, QFrame, QMessageBox, QApplication)
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QFont, QIcon
import logging

from .face_card import FaceCard
from .progress_dialog import ProgressDialog
from ..face_detector import FaceDetector
from ..face_swapper import FaceSwapper

logger = logging.getLogger(__name__)

class VideoProcessingThread(QThread):
    """Thread for processing video in background."""
    
    progress_updated = Signal(int, str)  # progress, message
    processing_finished = Signal(bool, str)  # success, message
    
    def __init__(self, video_path, output_path, face_detector, face_swapper):
        super().__init__()
        self.video_path = video_path
        self.output_path = output_path
        self.face_detector = face_detector
        self.face_swapper = face_swapper
        self.cancelled = False
    
    def cancel(self):
        """Cancel the processing."""
        self.cancelled = True
    
    def run(self):
        """Run the video processing."""
        try:
            import cv2
            
            # Open video
            cap = cv2.VideoCapture(self.video_path)
            if not cap.isOpened():
                self.processing_finished.emit(False, f"Could not open video: {self.video_path}")
                return
            
            # Get video properties
            fps = int(cap.get(cv2.CAP_PROP_FPS))
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            
            # Create video writer
            fourcc = cv2.VideoWriter_fourcc(*'mp4v')
            out = cv2.VideoWriter(self.output_path, fourcc, fps, (width, height))
            
            frame_count = 0
            
            self.progress_updated.emit(0, "Starting video processing...")
            
            while True:
                if self.cancelled:
                    break
                
                ret, frame = cap.read()
                if not ret:
                    break
                
                # Process frame
                processed_frame = self.face_swapper.process_video_frame(
                    frame, self.face_detector, {}
                )
                
                # Write frame
                out.write(processed_frame)
                
                frame_count += 1
                progress = int((frame_count / total_frames) * 100)
                
                # Update progress every 10 frames
                if frame_count % 10 == 0:
                    self.progress_updated.emit(
                        progress, 
                        f"Processing frame {frame_count}/{total_frames}"
                    )
            
            # Clean up
            cap.release()
            out.release()
            
            if self.cancelled:
                # Remove partial output file
                if os.path.exists(self.output_path):
                    os.remove(self.output_path)
                self.processing_finished.emit(False, "Processing cancelled by user")
            else:
                self.progress_updated.emit(100, "Processing complete!")
                self.processing_finished.emit(True, f"Video saved to: {self.output_path}")
                
        except Exception as e:
            logger.error(f"Video processing error: {e}")
            self.processing_finished.emit(False, f"Processing failed: {str(e)}")

class FaceScanThread(QThread):
    """Thread for scanning video for faces."""
    
    progress_updated = Signal(int, str)  # progress, message
    scanning_finished = Signal(bool, list, str)  # success, faces, message
    
    def __init__(self, video_path, face_detector):
        super().__init__()
        self.video_path = video_path
        self.face_detector = face_detector
        self.cancelled = False
    
    def cancel(self):
        """Cancel the scanning."""
        self.cancelled = True
    
    def run(self):
        """Run the face scanning."""
        try:
            def progress_callback(progress):
                if not self.cancelled:
                    self.progress_updated.emit(
                        int(progress), 
                        f"Scanning video... {progress:.1f}%"
                    )
            
            # Scan video for faces
            unique_faces = self.face_detector.scan_video_for_faces(
                self.video_path, progress_callback
            )
            
            if self.cancelled:
                self.scanning_finished.emit(False, [], "Scanning cancelled by user")
            else:
                self.scanning_finished.emit(
                    True, 
                    unique_faces, 
                    f"Found {len(unique_faces)} unique faces"
                )
                
        except Exception as e:
            logger.error(f"Face scanning error: {e}")
            self.scanning_finished.emit(False, [], f"Scanning failed: {str(e)}")

class MainWindow(QMainWindow):
    """Main application window for FaceSwap."""
    
    def __init__(self):
        super().__init__()
        self.video_path = None
        self.face_detector = None
        self.face_swapper = None
        self.face_cards = []
        self.scan_thread = None
        self.process_thread = None
        
        self.setup_ui()
        self.initialize_engines()
    
    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle("FaceSwap - Local Face Swapping Tool")
        self.setMinimumSize(800, 600)
        self.resize(1000, 700)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Title
        title_label = QLabel("FaceSwap - Local Video Face Swapping")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        main_layout.addWidget(title_label)
        
        # Instructions
        instructions = QLabel(
            "1. Select a video file  →  2. Scan for faces  →  3. Assign swap images  →  4. Process video"
        )
        instructions.setAlignment(Qt.AlignCenter)
        instructions.setStyleSheet("color: #7f8c8d; font-size: 12px; margin-bottom: 15px;")
        main_layout.addWidget(instructions)
        
        # Video selection section
        video_section = self.create_video_section()
        main_layout.addWidget(video_section)
        
        # Face scanning section
        scan_section = self.create_scan_section()
        main_layout.addWidget(scan_section)
        
        # Faces display section
        faces_section = self.create_faces_section()
        main_layout.addWidget(faces_section)
        
        # Processing section
        process_section = self.create_process_section()
        main_layout.addWidget(process_section)
        
        # Status bar
        self.statusBar().showMessage("Ready - Select a video file to begin")
    
    def create_video_section(self):
        """Create video selection section."""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Section title
        title = QLabel("Step 1: Select Video")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #34495e;")
        layout.addWidget(title)
        
        # Video path display and button
        video_layout = QHBoxLayout()
        
        self.video_label = QLabel("No video selected")
        self.video_label.setStyleSheet("""
            QLabel {
                border: 1px solid #bdc3c7;
                padding: 8px;
                background-color: #ecf0f1;
                border-radius: 4px;
            }
        """)
        video_layout.addWidget(self.video_label, 1)
        
        self.select_video_button = QPushButton("Select Video")
        self.select_video_button.clicked.connect(self.select_video)
        self.select_video_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #21618c;
            }
        """)
        video_layout.addWidget(self.select_video_button)
        
        layout.addLayout(video_layout)
        return frame
    
    def create_scan_section(self):
        """Create face scanning section."""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Section title
        title = QLabel("Step 2: Scan for Faces")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #34495e;")
        layout.addWidget(title)
        
        # Scan button and status
        scan_layout = QHBoxLayout()
        
        self.scan_status_label = QLabel("Ready to scan - Select a video first")
        self.scan_status_label.setStyleSheet("color: #7f8c8d;")
        scan_layout.addWidget(self.scan_status_label, 1)
        
        self.scan_button = QPushButton("Scan Video for Faces")
        self.scan_button.clicked.connect(self.scan_faces)
        self.scan_button.setEnabled(False)
        self.scan_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
            QPushButton:pressed {
                background-color: #a93226;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        scan_layout.addWidget(self.scan_button)
        
        layout.addLayout(scan_layout)
        return frame
    
    def create_faces_section(self):
        """Create faces display section."""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Section title
        title = QLabel("Step 3: Assign Swap Images")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #34495e;")
        layout.addWidget(title)
        
        # Scroll area for face cards
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMinimumHeight(200)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #bdc3c7;
                background-color: #f8f9fa;
                border-radius: 4px;
            }
        """)
        
        # Widget to contain the grid of face cards
        self.faces_widget = QWidget()
        self.faces_layout = QGridLayout(self.faces_widget)
        self.faces_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.faces_layout.setSpacing(10)
        
        self.scroll_area.setWidget(self.faces_widget)
        layout.addWidget(self.scroll_area)
        
        # Placeholder label
        self.no_faces_label = QLabel("No faces detected yet - Scan a video first")
        self.no_faces_label.setAlignment(Qt.AlignCenter)
        self.no_faces_label.setStyleSheet("color: #95a5a6; font-style: italic; padding: 50px;")
        self.faces_layout.addWidget(self.no_faces_label, 0, 0)
        
        return frame
    
    def create_process_section(self):
        """Create video processing section."""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Section title
        title = QLabel("Step 4: Process Video")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #34495e;")
        layout.addWidget(title)
        
        # Process button and status
        process_layout = QHBoxLayout()
        
        self.process_status_label = QLabel("Ready to process - Complete steps 1-3 first")
        self.process_status_label.setStyleSheet("color: #7f8c8d;")
        process_layout.addWidget(self.process_status_label, 1)
        
        self.process_button = QPushButton("Process Video")
        self.process_button.clicked.connect(self.process_video)
        self.process_button.setEnabled(False)
        self.process_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:pressed {
                background-color: #1e8449;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        process_layout.addWidget(self.process_button)
        
        layout.addLayout(process_layout)
        return frame
    
    def initialize_engines(self):
        """Initialize face detection and swapping engines."""
        try:
            self.face_detector = FaceDetector()
            self.face_swapper = FaceSwapper()
            logger.info("Face detection and swapping engines initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize engines: {e}")
            QMessageBox.critical(
                self, 
                "Initialization Error", 
                f"Failed to initialize face processing engines:\n\n{str(e)}\n\n"
                "Please ensure the required model files are installed in the 'models' directory."
            )
            sys.exit(1)
    
    def select_video(self):
        """Open file dialog to select video."""
        file_dialog = QFileDialog(self)
        file_dialog.setWindowTitle("Select Video File")
        file_dialog.setNameFilter("Video Files (*.mp4 *.avi *.mov *.mkv *.wmv *.flv)")
        file_dialog.setFileMode(QFileDialog.ExistingFile)
        
        if file_dialog.exec():
            selected_files = file_dialog.selectedFiles()
            if selected_files:
                self.video_path = selected_files[0]
                filename = os.path.basename(self.video_path)
                self.video_label.setText(filename)
                
                # Enable scan button
                self.scan_button.setEnabled(True)
                self.scan_status_label.setText("Ready to scan for faces")
                
                # Clear previous results
                self.clear_faces()
                
                self.statusBar().showMessage(f"Video selected: {filename}")
                logger.info(f"Video selected: {self.video_path}")
    
    def scan_faces(self):
        """Start face scanning process."""
        if not self.video_path or not os.path.exists(self.video_path):
            QMessageBox.warning(self, "Error", "Please select a valid video file first.")
            return
        
        # Create and show progress dialog
        self.progress_dialog = ProgressDialog(
            title="Scanning Video",
            message="Analyzing video frames to detect unique faces...",
            cancelable=True,
            parent=self
        )
        
        # Create and start scanning thread
        self.scan_thread = FaceScanThread(self.video_path, self.face_detector)
        self.scan_thread.progress_updated.connect(self.progress_dialog.update_progress)
        self.scan_thread.scanning_finished.connect(self.on_scanning_finished)
        
        # Connect cancel signal
        self.progress_dialog.cancel_requested.connect(self.scan_thread.cancel)
        
        # Start scanning
        self.scan_thread.start()
        self.progress_dialog.start_progress()
        self.progress_dialog.exec()
    
    def on_scanning_finished(self, success, faces, message):
        """Handle scanning completion."""
        self.progress_dialog.finish_progress(success, message)
        
        if success and faces:
            self.display_faces(faces)
            self.scan_status_label.setText(f"Scanning complete - Found {len(faces)} unique faces")
            self.statusBar().showMessage(f"Scanning complete - Found {len(faces)} unique faces")
            logger.info(f"Face scanning completed - Found {len(faces)} unique faces")
        else:
            self.scan_status_label.setText("Scanning failed or cancelled")
            if not success:
                QMessageBox.warning(self, "Scanning Error", message)
        
        # Clean up thread
        if self.scan_thread:
            self.scan_thread.quit()
            self.scan_thread.wait()
            self.scan_thread = None
    
    def display_faces(self, faces):
        """Display detected faces in the grid."""
        # Clear existing faces
        self.clear_faces()
        
        # Create face cards
        cols = 4  # Number of columns in grid
        for i, face_data in enumerate(faces):
            row = i // cols
            col = i % cols
            
            face_card = FaceCard(i, face_data, self)
            face_card.swap_image_selected.connect(self.on_swap_image_selected)
            
            self.faces_layout.addWidget(face_card, row, col)
            self.face_cards.append(face_card)
        
        # Update process button state
        self.update_process_button_state()
    
    def clear_faces(self):
        """Clear all face cards from the display."""
        # Remove face cards
        for face_card in self.face_cards:
            self.faces_layout.removeWidget(face_card)
            face_card.deleteLater()
        
        self.face_cards.clear()
        
        # Show placeholder if no faces
        if not self.face_cards:
            self.no_faces_label.setVisible(True)
            self.faces_layout.addWidget(self.no_faces_label, 0, 0)
        
        # Update process button state
        self.update_process_button_state()
    
    def on_swap_image_selected(self, face_index, image_path):
        """Handle swap image selection."""
        try:
            if image_path and os.path.exists(image_path):
                # Set swap image in face detector
                self.face_detector.set_swap_image(face_index, image_path)
                logger.info(f"Swap image set for face {face_index}: {os.path.basename(image_path)}")
            else:
                # Clear swap image
                if face_index < len(self.face_detector.unique_faces):
                    self.face_detector.unique_faces[face_index]['swap_image_path'] = None
                    self.face_detector.unique_faces[face_index]['swap_image'] = None
                    self.face_detector.unique_faces[face_index]['swap_landmarks'] = None
                logger.info(f"Swap image cleared for face {face_index}")
            
            # Update process button state
            self.update_process_button_state()
            
        except Exception as e:
            logger.error(f"Error setting swap image: {e}")
            QMessageBox.warning(self, "Error", f"Failed to set swap image:\n{str(e)}")
    
    def update_process_button_state(self):
        """Update the process button enabled state."""
        if self.face_detector and self.face_detector.is_ready_for_processing():
            self.process_button.setEnabled(True)
            self.process_status_label.setText("Ready to process video")
        else:
            self.process_button.setEnabled(False)
            if not self.face_cards:
                self.process_status_label.setText("Ready to process - Complete steps 1-3 first")
            else:
                missing_count = sum(1 for card in self.face_cards if not card.has_swap_image())
                if missing_count > 0:
                    self.process_status_label.setText(f"Assign swap images to {missing_count} more faces")
    
    def process_video(self):
        """Start video processing."""
        if not self.face_detector or not self.face_detector.is_ready_for_processing():
            QMessageBox.warning(self, "Error", "Please complete all previous steps first.")
            return
        
        # Get output path
        output_path = os.path.expanduser("~/Videos/faceswap_output.mp4")
        
        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        # Create and show progress dialog
        self.progress_dialog = ProgressDialog(
            title="Processing Video",
            message="Applying face swaps to video frames...",
            cancelable=True,
            parent=self
        )
        
        # Create and start processing thread
        self.process_thread = VideoProcessingThread(
            self.video_path, output_path, self.face_detector, self.face_swapper
        )
        self.process_thread.progress_updated.connect(self.progress_dialog.update_progress)
        self.process_thread.processing_finished.connect(self.on_processing_finished)
        
        # Connect cancel signal
        self.progress_dialog.cancel_requested.connect(self.process_thread.cancel)
        
        # Start processing
        self.process_thread.start()
        self.progress_dialog.start_progress()
        self.progress_dialog.exec()
    
    def on_processing_finished(self, success, message):
        """Handle processing completion."""
        self.progress_dialog.finish_progress(success, message)
        
        if success:
            self.process_status_label.setText("Processing complete!")
            self.statusBar().showMessage("Video processing completed successfully")
            
            # Show success message with option to open output directory
            reply = QMessageBox.question(
                self,
                "Processing Complete",
                f"{message}\n\nWould you like to open the output folder?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                import subprocess
                import platform
                
                output_dir = os.path.expanduser("~/Videos")
                if platform.system() == "Linux":
                    subprocess.run(["xdg-open", output_dir])
                elif platform.system() == "Darwin":  # macOS
                    subprocess.run(["open", output_dir])
                elif platform.system() == "Windows":
                    subprocess.run(["explorer", output_dir])
        else:
            self.process_status_label.setText("Processing failed or cancelled")
            if "cancelled" not in message.lower():
                QMessageBox.warning(self, "Processing Error", message)
        
        # Clean up thread
        if self.process_thread:
            self.process_thread.quit()
            self.process_thread.wait()
            self.process_thread = None
    
    def closeEvent(self, event):
        """Handle application close event."""
        # Cancel any running operations
        if self.scan_thread and self.scan_thread.isRunning():
            self.scan_thread.cancel()
            self.scan_thread.quit()
            self.scan_thread.wait()
        
        if self.process_thread and self.process_thread.isRunning():
            self.process_thread.cancel()
            self.process_thread.quit()
            self.process_thread.wait()
        
        event.accept()