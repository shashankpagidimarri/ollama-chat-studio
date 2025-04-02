import sys
import json
import base64
import requests
from datetime import datetime
from pathlib import Path
from database import DatabaseManager
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QTextEdit, QPushButton, QSplitter, QComboBox, 
                            QLabel, QFileDialog, QScrollArea, QCheckBox,
                            QStatusBar, QProgressBar, QMenu, QMenuBar,
                            QToolBar, QDialog, QFrame, QSizePolicy, QMessageBox,QApplication)
from PyQt6.QtCore import Qt, QSize, QTimer
from PyQt6.QtGui import QPixmap, QIcon, QFont, QAction
from PyQt6.QtCore import QPropertyAnimation, QRect
# Import our modules
from ui.message_widget import MessageWidget
# In main_window.py
from ui.dialogs import ModelParamsDialog, ConversationSettingsDialog, ConversationHistoryDialog
from ui.theme import apply_theme
from api.ollama_worker import OllamaWorker
from config import load_config, save_config

class OllamaChatUI(QMainWindow):
    """Main window for Ollama Chat UI application"""
    def __init__(self):
        super().__init__()
        # Load configuration
        config = load_config()
        
        # Initialize state
        self.conversation = []
        self.current_image = None
        self.model_params = config["model_params"]
        self.conversation_settings = config["conversation_settings"]
        self.ui_settings = config["ui_settings"]
        self.api_settings = config["api_settings"]
        self.current_conversation_id = None
        
        # Initialize database
        self.db = DatabaseManager()
        
        # Setup auto-save timer
        self.auto_save_timer = QTimer(self)
        self.auto_save_timer.timeout.connect(self.auto_save_conversation)
        
        # Start auto-save timer (60000 ms = 1 minute)
        self.auto_save_interval = 60000  # 1 minute in milliseconds
        self.auto_save_timer.start(self.auto_save_interval)
        
        # Initialize UI
        self.init_ui()
        
    def init_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Ollama Chat Studio")
        self.setGeometry(100, 100, 
                         self.ui_settings["window_width"], 
                         self.ui_settings["window_height"])
        self.setObjectName("mainWindow")  # For CSS styling
        
        # Apply theme based on settings
        apply_theme(self, self.ui_settings["dark_theme"])
        
        # Create central widget and main layout
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(12, 12, 12, 12)
        main_layout.setSpacing(8)
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create toolbar
        self.create_toolbar()
        
        # Create main content area with splitter
        splitter = QSplitter(Qt.Orientation.Vertical)
        
        # Create chat area
        chat_widget = self.create_chat_area()
        splitter.addWidget(chat_widget)
        
        # Create input area
        input_widget = self.create_input_area()
        splitter.addWidget(input_widget)
        
        # Set split proportions (70% chat, 30% input)
        splitter.setSizes([700, 300])
        
        # Add splitter to main layout
        main_layout.addWidget(splitter)
        
        # Create status bar
        self.create_status_bar()
        
        # Add a welcome message
        welcome_msg = self.conversation_settings["system_prompt"]
        self.add_message("Hello! I'm your Ollama-powered assistant. How can I help you today?", is_user=False)
        
        # Initialize by fetching models
        self.refresh_models()
        
    # In main_window.py, update the create_menu_bar method
    def auto_save_conversation(self):
        """Automatically save the current conversation"""
        # Only auto-save if we have messages and auto-save is enabled in settings
        if self.conversation and self.conversation_settings.get("auto_save", True):
            # Use the existing save method
            self.save_current_conversation()
            
            # Don't show a status message for auto-save to avoid disrupting the user
            # But we could log it if needed
            print(f"Auto-saved conversation at {datetime.now().strftime('%H:%M:%S')}")
    def create_menu_bar(self):
        """Create the application menu bar"""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu("&File")
        
        new_chat_action = QAction("New Chat", self)
        new_chat_action.setShortcut("Ctrl+N")
        new_chat_action.triggered.connect(self.new_chat)
        file_menu.addAction(new_chat_action)
        
        file_menu.addSeparator()
        
        # Add conversation history action
        history_action = QAction("Conversation History...", self)
        history_action.setShortcut("Ctrl+H")
        history_action.triggered.connect(self.show_conversation_history)
        file_menu.addAction(history_action)
        
        save_chat_action = QAction("Save Chat", self)
        save_chat_action.setShortcut("Ctrl+S")
        save_chat_action.triggered.connect(self.save_current_conversation)
        file_menu.addAction(save_chat_action)
        
        file_menu.addSeparator()
        
        exit_action = QAction("Exit", self)
        exit_action.setShortcut("Ctrl+Q")
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
    # Rest of the method remains the same...
        
    def create_toolbar(self):
        """Create the main toolbar with icons and styled controls"""
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setIconSize(QSize(18, 18))
        toolbar.setStyleSheet("""
            QToolBar {
                background-color: #202123;
                border-bottom: 1px solid #2D3748;
                spacing: 5px;
                padding: 5px;
            }
            QToolButton {
                background-color: transparent;
                border-radius: 4px;
                padding: 4px;
            }
            QToolButton:hover {
                background-color: rgba(255, 255, 255, 0.1);
            }
            QToolButton:pressed {
                background-color: rgba(255, 255, 255, 0.05);
            }
        """)
        self.addToolBar(toolbar)
        
        # Model selector label
        model_label = QLabel("Model:")
        model_label.setStyleSheet("color: #E2E8F0; margin-right: 5px;")
        toolbar.addWidget(model_label)
        
        # Model selector dropdown
        self.model_selector = QComboBox()
        self.model_selector.setMinimumWidth(150)
        self.model_selector.setStyleSheet("""
            QComboBox {
                background-color: #2D3748;
                color: white;
                border-radius: 4px;
                padding: 4px 8px;
                border: 1px solid #4A5568;
                min-width: 150px;
            }
            QComboBox::drop-down {
                border: none;
                padding-right: 15px;
            }
            QComboBox::down-arrow {
                width: 10px;
                height: 10px;
                image: url(icons/down-arrow.png);
            }
            QComboBox QAbstractItemView {
                background-color: #2D3748;
                color: white;
                selection-background-color: #10a37f;
                border: 1px solid #4A5568;
            }
        """)
        toolbar.addWidget(self.model_selector)
        
        # Refresh button
        refresh_action = QAction(QIcon("icons/refresh.png"), "Refresh Models", self)
        refresh_action.setToolTip("Refresh available models")
        refresh_action.triggered.connect(self.refresh_models)
        toolbar.addAction(refresh_action)
        
        # Add spacer
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Preferred)
        toolbar.addWidget(spacer)
        
        # Parameters button
        params_action = QAction(QIcon("icons/settings.png"), "Model Parameters", self)
        params_action.setToolTip("Adjust model parameters")
        params_action.triggered.connect(self.show_model_params)
        toolbar.addAction(params_action)
        
        # Add streaming toggle with custom styling
        self.stream_checkbox = QCheckBox("Enable streaming")
        self.stream_checkbox.setChecked(True)
        self.stream_checkbox.setStyleSheet("""
            QCheckBox {
                color: #E2E8F0;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                border-radius: 3px;
                border: 1px solid #4A5568;
            }
            QCheckBox::indicator:unchecked {
                background-color: #2D3748;
            }
            QCheckBox::indicator:checked {
                background-color: #10a37f;
                border: 1px solid #10a37f;
                image: url(icons/check.png);
            }
            QCheckBox::indicator:hover {
                border: 1px solid #10a37f;
            }
        """)
        toolbar.addWidget(self.stream_checkbox)
        
        return toolbar
        
    def create_chat_area(self):
        """Create the chat message area"""
        # Container for chat history
        self.chat_container = QWidget()
        self.chat_layout = QVBoxLayout(self.chat_container)
        self.chat_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.chat_layout.setSpacing(10)
        
        # Scrollable area
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.chat_container)
        
        return scroll_area
    
    def create_input_area(self):
        """Create the text input area with enhanced styling"""
        input_widget = QWidget()
        input_layout = QVBoxLayout(input_widget)
        
        # Image and text input
        img_input_layout = QHBoxLayout()
        
        # Image preview with improved styling
        self.image_preview = QLabel("No image")
        self.image_preview.setFixedSize(40, 40)
        self.image_preview.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.image_preview.setStyleSheet("""
            background-color: #2D3748; 
            border-radius: 5px;
            border: 1px solid #4A5568;
            color: #A0AEC0;
            font-size: 10px;
        """)
        img_input_layout.addWidget(self.image_preview)
        
        # Image upload button with icon
        img_button = QPushButton("Add Image")
        img_button.setIcon(QIcon("icons/image.png"))
        img_button.setObjectName("secondaryButton")
        img_button.setStyleSheet("""
            QPushButton#secondaryButton {
                background-color: #2D3748;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
                border: 1px solid #4A5568;
            }
            QPushButton#secondaryButton:hover {
                background-color: #3C4A5B;
            }
            QPushButton#secondaryButton:pressed {
                background-color: #253244;
            }
        """)
        img_button.clicked.connect(self.upload_image)
        img_input_layout.addWidget(img_button)
        
        # Clear image button with icon
        clear_img_button = QPushButton("Clear Image")
        clear_img_button.setIcon(QIcon("icons/clear.png"))
        clear_img_button.setObjectName("secondaryButton")
        clear_img_button.setStyleSheet("""
            QPushButton#secondaryButton {
                background-color: #2D3748;
                color: white;
                border-radius: 4px;
                padding: 6px 12px;
                border: 1px solid #4A5568;
            }
            QPushButton#secondaryButton:hover {
                background-color: #3C4A5B;
            }
            QPushButton#secondaryButton:pressed {
                background-color: #253244;
            }
        """)
        clear_img_button.clicked.connect(self.clear_image)
        img_input_layout.addWidget(clear_img_button)
        
        img_input_layout.addStretch()
        
        # Add image controls to main input layout
        input_layout.addLayout(img_input_layout)
        
        # Text input and send button
        text_input_layout = QHBoxLayout()
        
        # Text input field with improved styling
        self.input_field = QTextEdit()
        self.input_field.setObjectName("inputField")
        self.input_field.setPlaceholderText("Type your message here...")
        self.input_field.setMinimumHeight(80)
        self.input_field.setStyleSheet("""
            QTextEdit#inputField {
                background-color: #2D3748;
                color: white;
                border-radius: 10px;
                border: 1px solid #4A5568;
                padding: 8px 12px;
                selection-background-color: #10a37f;
            }
            QTextEdit#inputField:focus {
                border: 1px solid #10a37f;
            }
        """)
        text_input_layout.addWidget(self.input_field)
        
        # Send button with icon
        send_button = QPushButton("Send")
        send_button.setIcon(QIcon("icons/send.png"))
        send_button.setMinimumWidth(100)
        send_button.setStyleSheet("""
            QPushButton {
                background-color: #10a37f;
                color: white;
                border-radius: 10px;
                padding: 10px 15px;
                border: none;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0D8B6C;
            }
            QPushButton:pressed {
                background-color: #0A725A;
            }
        """)
        send_button.clicked.connect(self.send_message)
        text_input_layout.addWidget(send_button)
        
        input_layout.addLayout(text_input_layout)
        
        return input_widget

    def save_current_conversation(self):
    
        if not self.conversation:
            self.status_message.setText("Nothing to save")
            return
        
        # Check if we have a current conversation ID
        if hasattr(self, 'current_conversation_id') and self.current_conversation_id:
            # Update existing conversation
            success = self.db.update_conversation(
                conversation_id=self.current_conversation_id,
                messages=self.conversation
            )
            
            if success:
                self.status_message.setText(f"Conversation updated (ID: {self.current_conversation_id})")
                return self.current_conversation_id
            # If update fails, fall through to creating a new one
        
        # Generate a title from the first user message
        title = "New Conversation"
        for msg in self.conversation:
            if msg["role"] == "user":
                # Use the first 30 chars of the first user message as title
                title = msg["content"][:30] + "..." if len(msg["content"]) > 30 else msg["content"]
                break
        
        # Get the current model
        model = self.model_selector.currentText()
        
        # Save as a new conversation
        conversation_id = self.db.save_conversation(
            title=title,
            model=model,
            messages=self.conversation,
            system_prompt=self.conversation_settings["system_prompt"]
        )
        
        # Store the ID for future updates
        self.current_conversation_id = conversation_id
        
        self.status_message.setText(f"Conversation saved (ID: {conversation_id})")
        return conversation_id

    def load_conversation(self, conversation_id):
        """Load a conversation from the database"""
        conversation = self.db.get_conversation(conversation_id)
        
        if not conversation:
            self.status_message.setText(f"Conversation not found: {conversation_id}")
            return False
        
        # Clear current chat
        self.new_chat()  # This will reset current_conversation_id
        
        # Set the current conversation ID to the loaded one
        self.current_conversation_id = conversation_id
        
        # Load the conversation data
        self.conversation = conversation["messages"]
        
        # Update the UI with messages
        for msg in self.conversation:
            is_user = msg["role"] == "user"
            content = msg["content"]
            
            # Handle messages with images
            if isinstance(content, dict) and "image_path" in content:
                # TODO: Handle displaying images from saved conversations
                # For now, just show the text portion
                self.add_message(content["text"], is_user=is_user)
            else:
                self.add_message(content, is_user=is_user)
        
        # Update status
        self.status_message.setText(f"Loaded conversation: {conversation['title']}")
        return True

    def show_conversation_history(self):
        """Show dialog with conversation history"""
        # This will need a new dialog - we'll implement it later
        conversations = self.db.list_conversations(limit=50)
        
        # For now, just show the list in a message box
        if not conversations:
            QMessageBox.information(self, "Conversation History", "No saved conversations found.")
            return
        
        # Create and show the dialog (we'll implement this later)
        dialog = ConversationHistoryDialog(conversations, self)
        if dialog.exec() == QDialog.DialogCode.Accepted and dialog.selected_conversation_id:
            self.load_conversation(dialog.selected_conversation_id)

    def create_status_bar(self):
        """Create a styled status bar"""
        status_bar = QStatusBar()
        status_bar.setStyleSheet("""
            QStatusBar {
                background-color: #1A202C;
                color: #CBD5E0;
                border-top: 1px solid #2D3748;
                padding: 2px 10px;
                font-size: 11px;
            }
        """)
        self.setStatusBar(status_bar)
        
        # Progress bar for generation with improved styling
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximumWidth(150)
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #4A5568;
                border-radius: 4px;
                text-align: center;
                background-color: #2D3748;
                color: white;
                height: 14px;
            }
            QProgressBar::chunk {
                background-color: #10a37f;
                border-radius: 3px;
            }
        """)
        status_bar.addPermanentWidget(self.progress_bar)
        
        # Status message
        self.status_message = QLabel("Ready")
        status_bar.addWidget(self.status_message)
        
    def add_message(self, text, is_user=True):
        """Add a message to the chat"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        message_widget = MessageWidget(is_user, text, timestamp)
        
        # Set timestamp visibility based on settings
        message_widget.set_show_timestamp(self.conversation_settings["show_timestamps"])
        
        # Connect regenerate button if it's an assistant message
        if not is_user and hasattr(message_widget, 'regenerate_btn'):
            message_widget.regenerate_btn.clicked.connect(
                lambda: self.regenerate_message(message_widget)
            )
        
        self.chat_layout.addWidget(message_widget)
        
        # Auto scroll to bottom
        QTimer.singleShot(100, self.scroll_to_bottom)
        
    def scroll_to_bottom(self):
   
        scroll_area = self.chat_container.parent()
        if isinstance(scroll_area, QScrollArea):
            # Use singleShot with 0ms delay to ensure UI has updated first
            QTimer.singleShot(0, lambda: scroll_area.verticalScrollBar().setValue(
                scroll_area.verticalScrollBar().maximum()
            ))
    
    def send_message(self):
        """Send the current message with button animation"""
        message = self.input_field.toPlainText().strip()
        if not message:
            return
        
        # Find the send button for animation
        send_button = None
        for child in self.findChildren(QPushButton):
            if child.text() == "Send":
                send_button = child
                break
        
        # Apply animation if found
        if send_button:
            animation = QPropertyAnimation(send_button, b"geometry")
            animation.setDuration(100)
            current_geometry = send_button.geometry()
            animation.setStartValue(current_geometry)
            
            # Slightly smaller for "pressed" effect
            pressed_geometry = QRect(
                current_geometry.x() + 2, 
                current_geometry.y() + 2,
                current_geometry.width() - 4, 
                current_geometry.height() - 4
            )
            animation.setEndValue(pressed_geometry)
            animation.start()
                
        # Add user message to UI
        self.add_message(message, is_user=True)
        
        # Clear input field
        self.input_field.clear()
        
        # Prepare image if any
        image_data = self.get_image_data()
        
        # Add to conversation history
        user_message = {"role": "user", "content": message}
        if image_data:
            user_message["images"] = [image_data]
        self.conversation.append(user_message)
        
        # Get selected model
        model = self.model_selector.currentText()
        
        # Create an empty message for the assistant's response if streaming
        if self.stream_checkbox.isChecked():
            self.add_message("", is_user=False)
        
        # Send to Ollama in a separate thread
        self.worker = OllamaWorker(
            model, 
            message, 
            self.conversation[:-1], 
            self.model_params,
            image_data, 
            self.api_settings["base_url"]
        )
        
        # Connect signals
        if self.stream_checkbox.isChecked():
            # Streaming mode - handle tokens as they arrive
            self.worker.token_received.connect(self.handle_token)
        else:
            # Remove the empty message we added if not streaming
            for i in reversed(range(self.chat_layout.count())):
                widget = self.chat_layout.itemAt(i).widget()
                if isinstance(widget, MessageWidget) and not widget.is_user:
                    if widget.get_text() == "":
                        widget.deleteLater()
                        break
        
        # Connect other signals
        self.worker.response_complete.connect(self.handle_response)
        self.worker.error_occurred.connect(self.handle_error)
        self.worker.progress_update.connect(self.update_progress)
        
        # Update status
        self.status_message.setText("Generating response...")
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        
        # Start worker
        self.worker.start()
        
        # Clear image after sending
        self.clear_image()
    
    def handle_response(self, response_text):
        """Handle the completed response"""
        # Add to conversation history
        self.conversation.append({"role": "assistant", "content": response_text})
        
        # If we're not streaming, add the complete message now
        if not self.stream_checkbox.isChecked():
            self.add_message(response_text, is_user=False)
                
        # Update status
        self.status_message.setText("Ready")
        self.progress_bar.setVisible(False)
        
        # Auto-save if enabled - now we can trigger it immediately after a response
        if self.conversation_settings.get("auto_save", True):
            self.auto_save_conversation()
    
    def handle_token(self, token):
    # Find the last message in the chat layout
        for i in reversed(range(self.chat_layout.count())):
            widget = self.chat_layout.itemAt(i).widget()
            if isinstance(widget, MessageWidget) and not widget.is_user:
                # Update the existing assistant message
                current_text = widget.get_text()
                widget.set_text(current_text + token)
                
                # Force scroll after each token update
                self.scroll_to_bottom()
                return
        
        # If we get here, we need to create a new message (first token)
        self.add_message(token, is_user=False)
    
    def handle_error(self, error_message):
        """Handle API errors"""
        self.add_message(f"ERROR: {error_message}", is_user=False)
        self.status_message.setText("Error occurred")
        self.progress_bar.setVisible(False)
    
    def update_progress(self, progress):
        """Update progress bar"""
        self.progress_bar.setValue(progress)
    
    def refresh_models(self):
        """Refresh the list of available Ollama models"""
        try:
            response = requests.get(f"{self.api_settings['base_url']}/api/tags")
            if response.status_code == 200:
                current_model = self.model_selector.currentText()
                
                models = [model['name'] for model in response.json()['models']]
                self.model_selector.clear()
                self.model_selector.addItems(models)
                
                # Restore previous selection if possible
                if current_model and current_model in models:
                    index = self.model_selector.findText(current_model)
                    if index >= 0:
                        self.model_selector.setCurrentIndex(index)
                
                self.status_message.setText(f"Found {len(models)} models")
            else:
                self.status_message.setText(f"Failed to get models: {response.status_code}")
        except Exception as e:
            self.add_message(f"Error connecting to Ollama: {str(e)}", is_user=False)
            self.status_message.setText("Connection error")
    
    def upload_image(self):
        """Upload an image for multimodal models"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select Image", "", "Images (*.png *.jpg *.jpeg)"
        )
        
        if file_path:
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                # Store the image path
                self.current_image = file_path
                
                # Scale for preview
                self.image_preview.setPixmap(pixmap.scaled(
                    40, 40, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation
                ))
                
                self.status_message.setText(f"Image loaded: {Path(file_path).name}")
            else:
                self.add_message("Failed to load the selected image.", is_user=False)
    
    def clear_image(self):
        """Clear the current image"""
        self.current_image = None
        self.image_preview.setText("No image")
        self.image_preview.setPixmap(QPixmap())
    
    def get_image_data(self):
        """Get base64 encoded image data"""
        if not self.current_image:
            return None
            
        try:
            with open(self.current_image, "rb") as image_file:
                return base64.b64encode(image_file.read()).decode('utf-8')
        except Exception as e:
            self.add_message(f"Error processing image: {str(e)}", is_user=False)
            return None
    
    def regenerate_message(self, message_widget):
        """Regenerate the last assistant message"""
        # Remove the last assistant message from conversation
        if self.conversation and self.conversation[-1]["role"] == "assistant":
            self.conversation.pop()
            
            # Get the last user message
            if self.conversation and self.conversation[-1]["role"] == "user":
                user_message = self.conversation[-1]["content"]
                
                # Remove the message widget
                message_widget.deleteLater()
                
                # Process the message again
                if self.stream_checkbox.isChecked():
                    self.add_message("", is_user=False)
                
                # Send to Ollama
                self.send_user_message(user_message)
    
    def send_user_message(self, message):
        """Send a user message programmatically"""
        # Get selected model
        model = self.model_selector.currentText()
        
        # Create an Ollama worker
        self.worker = OllamaWorker(
            model, 
            message, 
            self.conversation[:-1], 
            self.model_params,
            None,  # No image data for regeneration
            self.api_settings["base_url"]
        )
        
        # Connect signals
        if self.stream_checkbox.isChecked():
            self.worker.token_received.connect(self.handle_token)
            
        self.worker.response_complete.connect(self.handle_response)
        self.worker.error_occurred.connect(self.handle_error)
        self.worker.progress_update.connect(self.update_progress)
        
        # Update status
        self.status_message.setText("Regenerating response...")
        self.progress_bar.setValue(0)
        self.progress_bar.setVisible(True)
        
        # Start worker
        self.worker.start()
    
    def new_chat(self):
        """Start a new chat session"""
        # Clear conversation history
        self.conversation = []
        
        # Reset the current conversation ID
        self.current_conversation_id = None
        
        # Clear chat UI - remove all existing widgets
        for i in reversed(range(self.chat_layout.count())):
            widget = self.chat_layout.itemAt(i).widget()
            if widget:
                widget.deleteLater()
        
        # Force UI update before adding new content
        QApplication.processEvents()
        
        # Create a welcome message explicitly
        welcome_widget = MessageWidget(is_user=False, text="Hello! I'm your Ollama-powered assistant. How can I help you today?")
        self.chat_layout.addWidget(welcome_widget)
        
        # Add to conversation history to maintain context
        self.conversation.append({
            "role": "assistant", 
            "content": "Hello! I'm your Ollama-powered assistant. How can I help you today?"
        })
        
        # Force another UI update to ensure the message appears
        QApplication.processEvents()
        
        # Update status
        self.status_message.setText("New chat started")
    
    def save_chat(self):
        """Save the current chat to a file"""
        if not self.conversation:
            self.status_message.setText("Nothing to save")
            return
            
        # Get save path
        file_path, _ = QFileDialog.getSaveFileName(
            self, 
            "Save Chat", 
            f"{self.conversation_settings['save_path']}/chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json", 
            "JSON Files (*.json)"
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(self.conversation, f, indent=2)
                self.status_message.setText(f"Chat saved to {Path(file_path).name}")
            except Exception as e:
                self.status_message.setText(f"Error saving chat: {str(e)}")
    
    def auto_save_chat(self):
        """Automatically save the chat"""
        if not self.conversation:
            return
            
        # Create save directory if it doesn't exist
        save_dir = Path(self.conversation_settings['save_path'])
        save_dir.mkdir(exist_ok=True, parents=True)
        
        # Generate filename
        filename = f"chat_autosave_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        file_path = save_dir / filename
        
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(self.conversation, f, indent=2)
            self.status_message.setText(f"Chat auto-saved")
        except Exception as e:
            self.status_message.setText(f"Error auto-saving: {str(e)}")
    
    def toggle_theme(self):
        """Toggle between dark and light themes"""
        self.ui_settings["dark_theme"] = not self.ui_settings["dark_theme"]
        apply_theme(self, self.ui_settings["dark_theme"])
        
        # Update status message
        theme_name = "dark" if self.ui_settings["dark_theme"] else "light"
        self.status_message.setText(f"Switched to {theme_name} theme")
    
    def show_model_params(self):
        """Show dialog to adjust model parameters"""
        dialog = ModelParamsDialog(self.model_params, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.model_params = dialog.get_params()
            self.status_message.setText("Model parameters updated")
    
    def show_conversation_settings(self):
        """Show dialog to adjust conversation settings"""
        dialog = ConversationSettingsDialog(self.conversation_settings, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.conversation_settings = dialog.get_settings()
            
            # Update timestamp visibility for all messages
            for i in range(self.chat_layout.count()):
                widget = self.chat_layout.itemAt(i).widget()
                if isinstance(widget, MessageWidget):
                    widget.set_show_timestamp(self.conversation_settings["show_timestamps"])
            
            self.status_message.setText("Conversation settings updated")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(
            self,
            "About Ollama Chat Studio",
            "Ollama Chat Studio\n\n"
            "A modern UI for interacting with Ollama AI models.\n\n"
            "Version: 1.0.0"
        )
    
    def closeEvent(self, event):
        """Handle window close event"""
        # Stop the auto-save timer
        self.auto_save_timer.stop()
        
        # Final save before closing
        if self.conversation and self.conversation_settings.get("auto_save", True):
            self.save_current_conversation()
        
        # Save config
        config = {
            "model_params": self.model_params,
            "conversation_settings": self.conversation_settings,
            "ui_settings": self.ui_settings,
            "api_settings": self.api_settings
        }
        save_config(config)
        
        # Accept the close event
        event.accept()