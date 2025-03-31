from pathlib import Path
from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QSlider, 
                           QDialogButtonBox, QCheckBox, QLineEdit, QPushButton,
                           QTextEdit, QFileDialog,QListWidget,QListWidgetItem)
from PyQt6.QtCore import Qt
from datetime import datetime
class ModelParamsDialog(QDialog):
    """Dialog for adjusting model parameters like temperature, top_p, etc."""
    def __init__(self, params=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Model Parameters")
        self.setMinimumWidth(400)
        
        # Use provided params or defaults
        self.params = params or {
            "temperature": 0.7,
            "top_p": 0.9,
            "top_k": 40,
            "max_tokens": 2048
        }
        
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Temperature
        temp_layout = QHBoxLayout()
        temp_layout.addWidget(QLabel("Temperature:"))
        self.temp_slider = QSlider(Qt.Orientation.Horizontal)
        self.temp_slider.setRange(0, 100)
        self.temp_slider.setValue(int(self.params["temperature"] * 100))
        self.temp_slider.valueChanged.connect(self.update_temp_label)
        temp_layout.addWidget(self.temp_slider)
        self.temp_label = QLabel(f"{self.params['temperature']:.2f}")
        temp_layout.addWidget(self.temp_label)
        layout.addLayout(temp_layout)
        
        # Add explanation for temperature
        layout.addWidget(QLabel("Lower values make output more focused and deterministic."))
        layout.addSpacing(10)
        
        # Top P
        top_p_layout = QHBoxLayout()
        top_p_layout.addWidget(QLabel("Top P:"))
        self.top_p_slider = QSlider(Qt.Orientation.Horizontal)
        self.top_p_slider.setRange(0, 100)
        self.top_p_slider.setValue(int(self.params["top_p"] * 100))
        self.top_p_slider.valueChanged.connect(self.update_top_p_label)
        top_p_layout.addWidget(self.top_p_slider)
        self.top_p_label = QLabel(f"{self.params['top_p']:.2f}")
        top_p_layout.addWidget(self.top_p_label)
        layout.addLayout(top_p_layout)
        
        # Add explanation for top p
        layout.addWidget(QLabel("Sets a probability threshold for token selection."))
        layout.addSpacing(10)
        
        # Top K
        top_k_layout = QHBoxLayout()
        top_k_layout.addWidget(QLabel("Top K:"))
        self.top_k_slider = QSlider(Qt.Orientation.Horizontal)
        self.top_k_slider.setRange(0, 100)
        self.top_k_slider.setValue(self.params["top_k"])
        self.top_k_slider.valueChanged.connect(self.update_top_k_label)
        top_k_layout.addWidget(self.top_k_slider)
        self.top_k_label = QLabel(f"{self.params['top_k']}")
        top_k_layout.addWidget(self.top_k_label)
        layout.addLayout(top_k_layout)
        
        # Add explanation for top k
        layout.addWidget(QLabel("Limits token selection to the top K options."))
        layout.addSpacing(10)
        
        # Max tokens
        max_tokens_layout = QHBoxLayout()
        max_tokens_layout.addWidget(QLabel("Max Tokens:"))
        self.max_tokens_slider = QSlider(Qt.Orientation.Horizontal)
        self.max_tokens_slider.setRange(32, 4096)
        self.max_tokens_slider.setValue(self.params["max_tokens"])
        self.max_tokens_slider.valueChanged.connect(self.update_max_tokens_label)
        max_tokens_layout.addWidget(self.max_tokens_slider)
        self.max_tokens_label = QLabel(f"{self.params['max_tokens']}")
        max_tokens_layout.addWidget(self.max_tokens_label)
        layout.addLayout(max_tokens_layout)
        
        # Add explanation for max tokens
        layout.addWidget(QLabel("Maximum number of tokens to generate."))
        layout.addSpacing(10)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def update_temp_label(self, value):
        temp = value / 100
        self.temp_label.setText(f"{temp:.2f}")
        self.params["temperature"] = temp
        
    def update_top_p_label(self, value):
        top_p = value / 100
        self.top_p_label.setText(f"{top_p:.2f}")
        self.params["top_p"] = top_p
        
    def update_top_k_label(self, value):
        self.top_k_label.setText(f"{value}")
        self.params["top_k"] = value
        
    def update_max_tokens_label(self, value):
        self.max_tokens_label.setText(f"{value}")
        self.params["max_tokens"] = value
        
    def get_params(self):
        return self.params


class ConversationSettingsDialog(QDialog):
    """Dialog for conversation settings"""
    def __init__(self, settings=None, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Conversation Settings")
        self.setMinimumWidth(400)
        
        # Default settings
        self.settings = settings or {
            "system_prompt": "You are a helpful AI assistant.",
            "auto_save": True,
            "save_path": str(Path.home() / "ollama_chats"),
            "show_timestamps": True
        }
        
        self.init_ui()
        
    def init_ui(self):
        # This is your main layout for the dialog
        main_layout = QVBoxLayout(self)
        
        # System prompt
        system_layout = QVBoxLayout()
        system_layout.addWidget(QLabel("System Prompt:"))
        self.system_prompt = QTextEdit()
        self.system_prompt.setText(self.settings["system_prompt"])
        self.system_prompt.setFixedHeight(100)
        system_layout.addWidget(self.system_prompt)
        main_layout.addLayout(system_layout)
        
        # Auto save - Add this block
        auto_save_layout = QHBoxLayout()
        self.auto_save_check = QCheckBox("Auto-save conversations")
        self.auto_save_check.setChecked(self.settings.get("auto_save", True))
        auto_save_layout.addWidget(self.auto_save_check)
        main_layout.addLayout(auto_save_layout)  # Use main_layout here
        
        # Save path
        save_path_layout = QHBoxLayout()
        save_path_layout.addWidget(QLabel("Save Path:"))
        self.save_path_field = QLineEdit(self.settings["save_path"])
        save_path_layout.addWidget(self.save_path_field)
        browse_button = QPushButton("Browse")
        browse_button.clicked.connect(self.browse_path)
        save_path_layout.addWidget(browse_button)
        main_layout.addLayout(save_path_layout)
        
        # Show timestamps
        timestamp_layout = QHBoxLayout()
        self.timestamp_check = QCheckBox("Show message timestamps")
        self.timestamp_check.setChecked(self.settings["show_timestamps"])
        timestamp_layout.addWidget(self.timestamp_check)
        main_layout.addLayout(timestamp_layout)
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        main_layout.addWidget(button_box)
        
    def browse_path(self):
        path = QFileDialog.getExistingDirectory(self, "Select Save Directory", self.save_path_field.text())
        if path:
            self.save_path_field.setText(path)
            
    def get_settings(self):
        self.settings["system_prompt"] = self.system_prompt.toPlainText()
        self.settings["auto_save"] = self.auto_save_check.isChecked()
        self.settings["save_path"] = self.save_path_field.text()
        self.settings["show_timestamps"] = self.timestamp_check.isChecked()
        self.settings["auto_save"] = self.auto_save_check.isChecked()
        return self.settings
# Add this to dialogs.py

class ConversationHistoryDialog(QDialog):
    """Dialog for browsing conversation history"""
    def __init__(self, conversations, parent=None):
        super().__init__(parent)
        self.conversations = conversations
        self.selected_conversation_id = None
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Conversation History")
        self.setMinimumWidth(600)
        self.setMinimumHeight(400)
        
        layout = QVBoxLayout(self)
        
        # Search box
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Search:"))
        self.search_field = QLineEdit()
        self.search_field.setPlaceholderText("Search conversations...")
        self.search_field.textChanged.connect(self.filter_conversations)
        search_layout.addWidget(self.search_field)
        layout.addLayout(search_layout)
        
        # Conversation list
        self.list_widget = QListWidget()
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.itemDoubleClicked.connect(self.accept_selection)
        layout.addWidget(self.list_widget)
        
        # Populate list
        self.populate_list()
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Open | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept_selection)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def populate_list(self):
        """Populate the list with conversations"""
        self.list_widget.clear()
        
        for conv in self.conversations:
            # Format item text
            date = datetime.fromisoformat(conv['updated_at']).strftime('%Y-%m-%d %H:%M')
            text = f"{conv['title']} ({date}) - {conv['message_count']} messages"
            
            item = QListWidgetItem(text)
            item.setData(Qt.ItemDataRole.UserRole, conv['id'])
            self.list_widget.addItem(item)
    
    def filter_conversations(self, text):
        """Filter conversations by search text"""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if text.lower() in item.text().lower():
                item.setHidden(False)
            else:
                item.setHidden(True)
    
    def accept_selection(self):
        """Accept the selected conversation"""
        current_item = self.list_widget.currentItem()
        if current_item:
            self.selected_conversation_id = current_item.data(Qt.ItemDataRole.UserRole)
            self.accept()