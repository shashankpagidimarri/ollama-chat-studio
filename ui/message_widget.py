from datetime import datetime
from PyQt6.QtWidgets import (QFrame, QVBoxLayout, QHBoxLayout, QTextEdit, 
                           QLabel, QSizePolicy, QPushButton, QApplication)
from PyQt6.QtGui import QFont
from PyQt6.QtCore import Qt

class MessageWidget(QFrame):
    """Widget for displaying chat messages"""
    def __init__(self, is_user=True, text="", timestamp=None, parent=None):
        super().__init__(parent)
        self.is_user = is_user
        self.timestamp = timestamp or datetime.now().strftime("%H:%M:%S")
        self.show_timestamp = True
        self.text = text
        self.init_ui()
        
    def init_ui(self):
        self.setFrameShape(QFrame.Shape.StyledPanel)
        self.setLineWidth(1)
        
        # Set object name for styling based on message type
        self.setObjectName("userMessage" if self.is_user else "assistantMessage")
            
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(4)
        
        # Header layout with icon, role, and timestamp
        header_layout = QHBoxLayout()
        
        # Role icon
        icon_label = QLabel()
        icon_size = 20
        if self.is_user:
            icon_label.setText("👤")  # User icon
        else:
            icon_label.setText("🤖")  # Bot icon
        icon_label.setFixedSize(icon_size, icon_size)
        header_layout.addWidget(icon_label)
        
        # Role text
        role_label = QLabel("You" if self.is_user else "Ollama Assistant")
        role_label.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        header_layout.addWidget(role_label)
        
        # Timestamp
        self.time_label = QLabel(self.timestamp)
        self.time_label.setFont(QFont("Segoe UI", 8))
        self.time_label.setStyleSheet("color: rgba(255, 255, 255, 0.5);")
        header_layout.addWidget(self.time_label)
        
        # Push everything to the left
        header_layout.addStretch()
        
        # Add header to main layout
        main_layout.addLayout(header_layout)
        
        # Message content
        self.messageText = QTextEdit()
        self.messageText.setReadOnly(True)
        self.messageText.setMinimumHeight(40)
        self.messageText.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Minimum)
        
        # Set text color and styling via object name
        self.messageText.setObjectName("userMessageText" if self.is_user else "assistantMessageText")
        self.messageText.setStyleSheet("background-color: transparent; border: none;")
        
        # Set font
        self.messageText.setFont(QFont("Segoe UI", 10))
        
        # Set initial text if provided
        if self.text:
            self.set_text(self.text)
            
        main_layout.addWidget(self.messageText)
        
        # Action buttons layout
        action_layout = QHBoxLayout()
        action_layout.setContentsMargins(0, 4, 0, 0)
        
        # Copy button
        copy_btn = QPushButton("Copy")
        copy_btn.setObjectName("iconButton")
        copy_btn.setFixedSize(60, 24)
        copy_btn.clicked.connect(self.copy_text)
        action_layout.addWidget(copy_btn)
        
        # Only show regenerate for assistant messages
        if not self.is_user:
            regenerate_btn = QPushButton("Regenerate")
            regenerate_btn.setObjectName("iconButton")
            regenerate_btn.setFixedSize(90, 24)
            # We'll connect this in the main window
            self.regenerate_btn = regenerate_btn
            action_layout.addWidget(regenerate_btn)
        
        # Push buttons to the left
        action_layout.addStretch()
        
        main_layout.addLayout(action_layout)
        
    def set_text(self, text):
        self.text = text
        self.messageText.setPlainText(text)
        
        # Adjust height based on content
        document_height = self.messageText.document().size().height()
        self.messageText.setMinimumHeight(min(400, max(60, int(document_height + 30))))
        
        # Make sure vertical scrollbar appears if needed
        self.messageText.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        
        # Force layout update
        self.layout().update()
        
    def get_text(self):
        """Get the text content of the message"""
        return self.messageText.toPlainText()
        
    def copy_text(self):
        """Copy the message text to clipboard"""
        QApplication.clipboard().setText(self.messageText.toPlainText())
        
    def set_show_timestamp(self, show):
        """Toggle timestamp visibility"""
        self.show_timestamp = show
        self.time_label.setVisible(show)