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
        self.setLineWidth(0)  # Remove border line
        
        # Set object name for styling
        self.setObjectName("userMessage" if self.is_user else "assistantMessage")
        
        # Apply enhanced styling with gradients and shadows
        if self.is_user:
            self.setStyleSheet("""
                #userMessage {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #2A2F3B, stop:1 #353B48);
                    color: white;
                    border-radius: 12px;
                    margin: 2px 10px 2px 50px;  /* More space on the left */
                    padding: 2px;
                }
            """)
        else:
            self.setStyleSheet("""
                #assistantMessage {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #40454F, stop:1 #4A5568);
                    color: white;
                    border-radius: 12px;
                    margin: 2px 50px 2px 10px;  /* More space on the right */
                    padding: 2px;
                    border-left: 3px solid #10a37f;  /* Green accent like Claude */
                }
            """)
            
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(4)
        
        # Header layout with icon and role
        header_layout = QHBoxLayout()
        
        # Role icon
        icon_label = QLabel()
        icon_size = 20
        if self.is_user:
            icon_label.setText("👤")  # Replace with proper icon in resources
        else:
            icon_label.setText("🤖")  # Replace with proper icon in resources
        icon_label.setFixedSize(icon_size, icon_size)
        header_layout.addWidget(icon_label)
        
        # Role text
        role_label = QLabel("You" if self.is_user else "Assistant")
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
        
        # Enhanced text styling
        self.messageText.setStyleSheet("""
            background-color: transparent; 
            border: none;
            color: white;
            font-family: 'Segoe UI';
            padding: 5px;
        """)
        
        # Set font
        self.messageText.setFont(QFont("Segoe UI", 10))
        
        main_layout.addWidget(self.messageText)
        
        # Action buttons layout - (copy, regenerate, etc.)
        action_layout = QHBoxLayout()
        action_layout.setContentsMargins(0, 8, 0, 0)
        
        # Copy button with enhanced styling
        copy_btn = QPushButton("Copy")
        copy_btn.setObjectName("actionButton")
        copy_btn.setFixedSize(70, 28)
        copy_btn.setStyleSheet("""
            QPushButton#actionButton {
                background-color: rgba(255, 255, 255, 0.1);
                color: rgba(255, 255, 255, 0.8);
                border-radius: 4px;
                border: none;
                padding: 4px 8px;
                font-size: 9pt;
            }
            QPushButton#actionButton:hover {
                background-color: rgba(255, 255, 255, 0.2);
            }
            QPushButton#actionButton:pressed {
                background-color: rgba(255, 255, 255, 0.15);
            }
        """)
        copy_btn.clicked.connect(self.copy_text)
        action_layout.addWidget(copy_btn)
        
        # Only show regenerate for assistant messages
        if not self.is_user:
            regenerate_btn = QPushButton("Regenerate")
            regenerate_btn.setObjectName("actionButton")
            regenerate_btn.setFixedSize(90, 28)
            regenerate_btn.setStyleSheet("""
                QPushButton#actionButton {
                    background-color: rgba(255, 255, 255, 0.1);
                    color: rgba(255, 255, 255, 0.8);
                    border-radius: 4px;
                    border: none;
                    padding: 4px 8px;
                    font-size: 9pt;
                }
                QPushButton#actionButton:hover {
                    background-color: rgba(255, 255, 255, 0.2);
                }
                QPushButton#actionButton:pressed {
                    background-color: rgba(255, 255, 255, 0.15);
                }
            """)
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