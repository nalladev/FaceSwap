import sys
from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                               QPushButton, QProgressBar, QTextEdit, QFrame)
from PySide6.QtCore import Qt, Signal, QTimer, QThread, pyqtSignal
from PySide6.QtGui import QFont, QMovie
import logging

logger = logging.getLogger(__name__)

class ProgressDialog(QDialog):
    """
    Progress dialog for displaying progress of long-running operations.
    Shows progress bar, status messages, and optional cancel functionality.
    """
    
    # Signal emitted when cancel is requested
    cancel_requested = Signal()
    
    def __init__(self, title: str = "Processing", message: str = "Please wait...", 
                 cancelable: bool = True, parent=None):
        """
        Initialize progress dialog.
        
        Args:
            title: Dialog window title
            message: Initial message to display
            cancelable: Whether to show cancel button
            parent: Parent widget
        """
        super().__init__(parent)
        self.title = title
        self.initial_message = message
        self.cancelable = cancelable
        self.cancelled = False
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the user interface."""
        self.setWindowTitle(self.title)
        self.setModal(True)
        self.setFixedSize(450, 300)
        self.setWindowFlags(Qt.Dialog | Qt.WindowTitleHint)
        
        # Main layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Title label
        title_label = QLabel(self.title)
        title_font = QFont()
        title_font.setPointSize(14)
        title_font.setBold(True)
        title_label.setFont(title_font)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Status message
        self.status_label = QLabel(self.initial_message)
        self.status_label.setAlignment(Qt.AlignCenter)
        self.status_label.setWordWrap(True)
        self.status_label.setStyleSheet("color: #333333; font-size: 12px;")
        layout.addWidget(self.status_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setRange(0, 100)
        self.progress_bar.setValue(0)
        self.progress_bar.setTextVisible(True)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #cccccc;
                border-radius: 8px;
                text-align: center;
                font-weight: bold;
                height: 25px;
            }
            QProgressBar::chunk {
                background-color: #4CAF50;
                border-radius: 6px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Detailed status text area
        self.details_text = QTextEdit()
        self.details_text.setMaximumHeight(100)
        self.details_text.setReadOnly(True)
        self.details_text.setStyleSheet("""
            QTextEdit {
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: #f9f9f9;
                font-family: Consolas, monospace;
                font-size: 10px;
            }
        """)
        layout.addWidget(self.details_text)
        
        # Button layout
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        if self.cancelable:
            self.cancel_button = QPushButton("Cancel")
            self.cancel_button.clicked.connect(self.cancel_operation)
            self.cancel_button.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border: none;
                    padding: 10px 20px;
                    border-radius: 4px;
                    font-weight: bold;
                    min-width: 80px;
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
            button_layout.addWidget(self.cancel_button)
        
        # Close button (initially hidden)
        self.close_button = QPushButton("Close")
        self.close_button.clicked.connect(self.accept)
        self.close_button.setVisible(False)
        self.close_button.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 4px;
                font-weight: bold;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
        """)
        button_layout.addWidget(self.close_button)
        
        layout.addLayout(button_layout)
        
        # Timer for updating elapsed time
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_elapsed_time)
        self.start_time = None
        
    def start_progress(self):
        """Start the progress tracking."""
        self.cancelled = False
        self.progress_bar.setValue(0)
        self.timer.start(1000)  # Update every second
        from time import time
        self.start_time = time()
        
        if self.cancelable:
            self.cancel_button.setEnabled(True)
            
        logger.info(f"Progress dialog started: {self.title}")
    
    def update_progress(self, value: int, message: str = None):
        """
        Update the progress bar and message.
        
        Args:
            value: Progress value (0-100)
            message: Optional status message
        """
        if self.cancelled:
            return
            
        self.progress_bar.setValue(max(0, min(100, value)))
        
        if message:
            self.status_label.setText(message)
            self.add_detail(f"Progress {value}%: {message}")
    
    def add_detail(self, message: str):
        """
        Add a detailed message to the text area.
        
        Args:
            message: Message to add
        """
        from datetime import datetime
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}"
        
        self.details_text.append(formatted_message)
        
        # Auto-scroll to bottom
        cursor = self.details_text.textCursor()
        cursor.movePosition(cursor.End)
        self.details_text.setTextCursor(cursor)
    
    def update_elapsed_time(self):
        """Update elapsed time display."""
        if self.start_time:
            from time import time
            elapsed = int(time() - self.start_time)
            minutes = elapsed // 60
            seconds = elapsed % 60
            
            current_text = self.progress_bar.text()
            if "Elapsed:" not in current_text:
                elapsed_text = f" - Elapsed: {minutes:02d}:{seconds:02d}"
                # Update progress bar format to include elapsed time
                self.progress_bar.setFormat(f"%p%{elapsed_text}")
    
    def cancel_operation(self):
        """Handle cancel button click."""
        if not self.cancelled:
            self.cancelled = True
            self.cancel_button.setEnabled(False)
            self.cancel_button.setText("Cancelling...")
            self.status_label.setText("Cancelling operation...")
            self.add_detail("Cancel requested by user")
            
            # Emit cancel signal
            self.cancel_requested.emit()
            
            logger.info("Progress operation cancelled by user")
    
    def finish_progress(self, success: bool = True, message: str = None):
        """
        Finish the progress operation.
        
        Args:
            success: Whether the operation completed successfully
            message: Final status message
        """
        self.timer.stop()
        
        if success and not self.cancelled:
            self.progress_bar.setValue(100)
            final_message = message or "Operation completed successfully!"
            self.status_label.setText(final_message)
            self.add_detail(f"SUCCESS: {final_message}")
            
            # Change progress bar color to indicate success
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 2px solid #cccccc;
                    border-radius: 8px;
                    text-align: center;
                    font-weight: bold;
                    height: 25px;
                }
                QProgressBar::chunk {
                    background-color: #4CAF50;
                    border-radius: 6px;
                }
            """)
            
        elif self.cancelled:
            final_message = "Operation cancelled by user"
            self.status_label.setText(final_message)
            self.add_detail(f"CANCELLED: {final_message}")
            
            # Change progress bar color to indicate cancellation
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 2px solid #cccccc;
                    border-radius: 8px;
                    text-align: center;
                    font-weight: bold;
                    height: 25px;
                }
                QProgressBar::chunk {
                    background-color: #FF9800;
                    border-radius: 6px;
                }
            """)
            
        else:
            # Error case
            final_message = message or "Operation failed!"
            self.status_label.setText(final_message)
            self.add_detail(f"ERROR: {final_message}")
            
            # Change progress bar color to indicate error
            self.progress_bar.setStyleSheet("""
                QProgressBar {
                    border: 2px solid #cccccc;
                    border-radius: 8px;
                    text-align: center;
                    font-weight: bold;
                    height: 25px;
                }
                QProgressBar::chunk {
                    background-color: #f44336;
                    border-radius: 6px;
                }
            """)
        
        # Show close button and hide cancel button
        if self.cancelable:
            self.cancel_button.setVisible(False)
        self.close_button.setVisible(True)
        
        logger.info(f"Progress dialog finished - Success: {success}, Cancelled: {self.cancelled}")
    
    def is_cancelled(self) -> bool:
        """
        Check if the operation was cancelled.
        
        Returns:
            True if cancelled, False otherwise
        """
        return self.cancelled
    
    def set_indeterminate(self, indeterminate: bool = True):
        """
        Set progress bar to indeterminate mode.
        
        Args:
            indeterminate: True for indeterminate mode, False for normal mode
        """
        if indeterminate:
            self.progress_bar.setRange(0, 0)
        else:
            self.progress_bar.setRange(0, 100)
    
    def closeEvent(self, event):
        """Handle close event."""
        if not self.cancelled and self.cancelable:
            # If operation is still running, treat close as cancel
            self.cancel_operation()
        event.accept()