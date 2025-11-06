import sys
import os
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                               QLabel, QPushButton, QFileDialog, QScrollArea, 
                               QGridLayout, QFrame, QMessageBox, QApplication)
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtGui import QFont, QIcon
import logging

from gui.face_card import FaceCard
from gui.progress_dialog import ProgressDialog
from face_detector import FaceDetector
from face_swapper import FaceSwapper

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
        self.total_frames = 0
        self.faces_found = 0
    
    def cancel(self):
        """Cancel the scanning."""
        self.cancelled = True
    
    def run(self):
        """Run the face scanning."""
        try:
            # Get total frame count first
            import cv2
            cap = cv2.VideoCapture(self.video_path)
            if cap.isOpened():
                self.total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                cap.release()
            
            def progress_callback(progress):
                if not self.cancelled:
                    # Update faces found count from detector
                    self.faces_found = len(getattr(self.face_detector, 'unique_faces', []))
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
    
    def create_scan_progress_display(self):
        """Create inline progress display for face detection."""
        # Progress display (initially hidden)
        self.scan_progress_label = QLabel()
        self.scan_progress_label.setVisible(False)
        self.scan_progress_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                padding: 8px;
                border-radius: 4px;
                font-family: monospace;
                color: #495057;
                margin: 10px 0px;
            }
        """)
        return self.scan_progress_label
    
    def create_faces_section(self):
        """Create faces display section."""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Section title
        title = QLabel("Step 2: Assign Swap Images (Click + to add face images)")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #34495e;")
        layout.addWidget(title)
        
        # Add progress display for face detection
        progress_display = self.create_scan_progress_display()
        layout.addWidget(progress_display)
        
        # Scroll area for face cards with responsive wrapping
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setMinimumHeight(200)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: 1px solid #bdc3c7;
                background-color: #f8f9fa;
                border-radius: 4px;
            }
        """)
        
        # Widget to contain the flowing layout of face cards
        self.faces_widget = QWidget()
        # Use QGridLayout for responsive wrapping
        from PySide6.QtWidgets import QGridLayout
        self.faces_layout = QGridLayout(self.faces_widget)
        self.faces_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self.faces_layout.setSpacing(25)
        self.faces_layout.setContentsMargins(15, 15, 15, 15)
        
        self.scroll_area.setWidget(self.faces_widget)
        layout.addWidget(self.scroll_area)
        
        # Placeholder label
        self.no_faces_label = QLabel("No faces detected yet - Scan a video first")
        self.no_faces_label.setAlignment(Qt.AlignCenter)
        self.no_faces_label.setStyleSheet("color: #95a5a6; font-style: italic; padding: 50px;")
        self.faces_layout.addWidget(self.no_faces_label)
        
        return frame
    
    def create_process_section(self):
        """Create video processing section."""
        frame = QFrame()
        frame.setFrameStyle(QFrame.StyledPanel)
        layout = QVBoxLayout(frame)
        
        # Section title
        title = QLabel("Step 3: Process Video")
        title.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #34495e;")
        layout.addWidget(title)
        
        # Process button and status
        process_layout = QHBoxLayout()
        
        self.process_status_label = QLabel("Assign swap images to all faces to enable processing")
        self.process_status_label.setStyleSheet("color: #7f8c8d;")
        process_layout.addWidget(self.process_status_label, 1)
        
        self.process_button = QPushButton("🎬 Start Face Swap")
        self.process_button.clicked.connect(self.process_video)
        self.process_button.setEnabled(False)
        self.process_button.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                min-width: 180px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
            QPushButton:pressed {
                background-color: #7d3c98;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        process_layout.addWidget(self.process_button)
        
        # Open video button (initially hidden, replaces process button after completion)
        self.open_video_button = QPushButton("🎬 Open Video")
        self.open_video_button.clicked.connect(self.open_video_file)
        self.open_video_button.setVisible(False)
        self.open_video_button.setStyleSheet("""
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
                min-width: 180px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        process_layout.addWidget(self.open_video_button)

        layout.addLayout(process_layout)
        
        # Progress display (initially hidden)
        self.process_progress_label = QLabel()
        self.process_progress_label.setVisible(False)
        self.process_progress_label.setStyleSheet("""
            QLabel {
                background-color: #f8f9fa;
                border: 1px solid #dee2e6;
                padding: 10px;
                border-radius: 4px;
                font-family: monospace;
                color: #495057;
                margin-top: 10px;
            }
        """)
        layout.addWidget(self.process_progress_label)
        
        return frame
    
    def initialize_engines(self):
        """Initialize face detection and swapping engines."""
        try:
            self.face_detector = FaceDetector()
            self.face_swapper = FaceSwapper()
            
            # Create Videos/FaceSwap directory in user's home folder
            videos_dir = os.path.expanduser("~/Videos/FaceSwap")
            os.makedirs(videos_dir, exist_ok=True)
            logger.info(f"Created output directory: {videos_dir}")
            
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
        # Try to force native PopOS file dialog
        try:
            # First attempt: explicitly use native dialog
            dialog = QFileDialog(self)
            dialog.setFileMode(QFileDialog.ExistingFile)
            dialog.setNameFilter("Video Files (*.mp4 *.avi *.mov *.mkv *.wmv *.flv)")
            dialog.setWindowTitle("Select Video File")
            dialog.setOption(QFileDialog.DontUseNativeDialog, False)  # Force native
            
            if dialog.exec():
                video_path = dialog.selectedFiles()[0]
            else:
                video_path = None
        except:
            # Fallback to standard method
            video_path, _ = QFileDialog.getOpenFileName(
                self, 
                "Select Video File", 
                "", 
                "Video Files (*.mp4 *.avi *.mov *.mkv *.wmv *.flv);;All Files (*)"
            )
        
        if video_path:
            self.video_path = video_path
            filename = os.path.basename(self.video_path)
            self.video_label.setText(filename)
            
            # Clear previous results
            self.clear_faces()
            
            self.statusBar().showMessage(f"Video selected: {filename}")
            logger.info(f"Video selected: {self.video_path}")
            
            # Auto-start face scanning
            self.scan_faces()
    
    def scan_faces(self):
        """Start face scanning process."""
        if not self.video_path or not os.path.exists(self.video_path):
            QMessageBox.warning(self, "Error", "Please select a valid video file first.")
            return
        
        # Show inline progress
        self.scan_progress_label.setVisible(True)
        self.scan_progress_label.setText("Starting face detection...")
        
        # Create and start scanning thread
        self.scan_thread = FaceScanThread(self.video_path, self.face_detector)
        self.scan_thread.progress_updated.connect(self.update_scan_progress)
        self.scan_thread.scanning_finished.connect(self.on_scanning_finished)
        
        # Start scanning
        self.scan_thread.start()
    
    def update_scan_progress(self, value, message=None):
        """Update inline scan progress display."""
        if hasattr(self.scan_thread, 'total_frames') and self.scan_thread.total_frames > 0:
            faces_found = getattr(self.scan_thread, 'faces_found', 0)
            progress_text = f"🔍 Detecting faces: {value}% - {faces_found} unique faces found"
        else:
            progress_text = f"🔍 Detecting faces: {value}%"
            if message:
                progress_text += f" - {message}"
        
        self.scan_progress_label.setText(progress_text)
    
    def on_scanning_finished(self, success, faces, message):
        """Handle scanning completion."""
        # Hide progress display
        self.scan_progress_label.setVisible(False)
        
        if success and faces:
            self.display_faces(faces)
            self.statusBar().showMessage(f"Face detection complete - Found {len(faces)} unique faces")
            logger.info(f"Face scanning completed - Found {len(faces)} unique faces")
        else:
            if not success:
                logger.error(f"Face scanning failed: {message}")
                QMessageBox.warning(self, "Face Detection Failed", f"Face detection failed:\n{message}")
        
        # Clean up thread
        if self.scan_thread:
            self.scan_thread.quit()
            self.scan_thread.wait()
            self.scan_thread = None
    
    def display_faces(self, faces):
        """Display detected faces in horizontal layout."""
        # Clear existing faces
        self.clear_faces()
        
        # Hide the no-faces placeholder
        self.no_faces_label.setVisible(False)
        
        # Create face cards with responsive grid layout
        cols = 4  # Number of columns before wrapping (reduced for better spacing)
        for i, face_data in enumerate(faces):
            face_card = FaceCard(i, face_data, self)
            face_card.swap_image_selected.connect(self.on_swap_image_selected)
            
            row = i // cols
            col = i % cols
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
        
        # Get output path in user's Videos/FaceSwap folder
        input_filename = os.path.basename(self.video_path)
        name_part, ext = os.path.splitext(input_filename)
        output_filename = f"{name_part}_swapped{ext}"
        
        # Create Videos/FaceSwap directory in user's home folder
        videos_dir = os.path.expanduser("~/Videos/FaceSwap")
        os.makedirs(videos_dir, exist_ok=True)
        
        output_path = os.path.join(videos_dir, output_filename)
        
        # Show inline progress
        self.process_button.setEnabled(False)
        self.process_button.setText("Processing...")
        self.process_progress_label.setVisible(True)
        self.process_progress_label.setText("Starting video processing...")
        
        # Create and start processing thread
        self.process_thread = VideoProcessingThread(
            self.video_path, output_path, self.face_detector, self.face_swapper
        )
        self.process_thread.progress_updated.connect(self.update_process_progress)
        self.process_thread.processing_finished.connect(self.on_processing_finished)
        
        # Start processing
        self.process_thread.start()
    
    def update_process_progress(self, value, message=None):
        """Update inline process progress display."""
        if hasattr(self.process_thread, 'total_frames') and self.process_thread.total_frames > 0:
            current_frame = int(value * self.process_thread.total_frames / 100)
            progress_text = f"Processing frame {current_frame}/{self.process_thread.total_frames} ({value}%)"
            if message:
                progress_text += f" - {message}"
        else:
            progress_text = f"Processing: {value}%"
            if message:
                progress_text += f" - {message}"
        
        self.process_progress_label.setText(progress_text)
    
    def on_processing_finished(self, success, message):
        """Handle processing completion."""
        # Reset UI elements
        self.process_progress_label.setVisible(False)
        
        if success:
            # Get output path from user's Videos/FaceSwap folder
            videos_dir = os.path.expanduser("~/Videos/FaceSwap")
            
            # Try to find the output file
            input_filename = os.path.basename(self.video_path)
            name_part, ext = os.path.splitext(input_filename)
            output_filename = f"{name_part}_swapped{ext}"
            output_path = os.path.join(videos_dir, output_filename)
            
            if os.path.exists(output_path):
                self.process_status_label.setText(f"✅ Video saved to: ~/Videos/FaceSwap/{output_filename}")
                self.statusBar().showMessage("Video processing completed successfully")
                
                # Show open video button
                self.show_video_ready_button(output_path)
            else:
                self.process_status_label.setText("✅ Processing complete! Check ~/Videos/FaceSwap/ folder")
                self.statusBar().showMessage("Video processing completed successfully")
        else:
            # Re-enable button on failure
            self.process_button.setEnabled(True)
            self.process_button.setText("🎬 Start Face Swap")
            self.process_status_label.setText("❌ Processing failed")
            if "cancelled" not in message.lower():
                logger.error(f"Video processing failed: {message}")
                QMessageBox.warning(self, "Processing Failed", f"Video processing failed:\n{message}")
        
        # Clean up thread
        if self.process_thread:
            self.process_thread.quit()
            self.process_thread.wait()
            self.process_thread = None
    
    def show_video_ready_button(self, video_path):
        """Show the open video button in place of process button."""
        # Hide the process button and show open video button
        self.process_button.setVisible(False)
        self.open_video_button.setVisible(True)
        
        # Store video path for opening
        self.output_video_path = video_path
    
    def open_video_file(self):
        """Open video file with default system player."""
        try:
            import subprocess
            import platform
            
            video_path = getattr(self, 'output_video_path', None)
            if not video_path:
                QMessageBox.warning(self, "Error", "No video file to open.")
                return
            
            system = platform.system()
            if system == "Windows":
                os.startfile(video_path)
            elif system == "Darwin":  # macOS
                subprocess.run(["open", video_path])
            else:  # Linux
                subprocess.run(["xdg-open", video_path])
                
            logger.info(f"Opened video file: {video_path}")
        except Exception as e:
            logger.error(f"Failed to open video file: {e}")
            QMessageBox.information(
                self,
                "Video Ready",
                f"Your video is ready at:\n{getattr(self, 'output_video_path', 'Unknown location')}"
            )
    
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