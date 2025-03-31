from pathlib import Path

# Default configurations
DEFAULT_CONFIG = {
    # Model parameters
    "model_params": {
        "temperature": 0.7,
        "top_p": 0.9,
        "top_k": 40,
        "max_tokens": 2048
    },
    
    # Conversation settings
    "conversation_settings": {
        "system_prompt": "You are a helpful AI assistant.",
        "auto_save": True,
        "save_path": str(Path.home() / "ollama_chats"),
        "show_timestamps": True
    },
    
    # UI settings
    "ui_settings": {
        "dark_theme": True,
        "font_size": 10,
        "window_width": 1100,
        "window_height": 800
    },
    
    # API settings
    "api_settings": {
        "base_url": "http://localhost:11434",
        "timeout": 60
    }
}

# Function to load config from file (to be implemented)
def load_config():
    # In a real app, you would load from a config file
    # For now, we'll just return the default config
    return DEFAULT_CONFIG.copy()

# Function to save config to file (to be implemented)
def save_config(config):
    # In a real app, you would save to a config file
    pass