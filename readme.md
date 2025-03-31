# Ollama Chat Studio

A modern desktop application for interacting with Ollama AI models with a clean UI, customizable parameters, and conversation memory.

## Features

- **Clean Chat Interface** with styled message bubbles
- **Real-time Streaming** responses
- **Model Selection** for any Ollama model
- **Parameter Customization** (temperature, top_p, etc.)
- **Dark/Light Themes**
- **Image Support** for multimodal models
- **Conversation Memory** using SQLite
- **Auto-save functionality**
- **Regenerate and Copy options**

## Installation

```bash
# Clone repository
git clone https://github.com/yourusername/ollama-chat-studio.git
cd ollama-chat-studio

# Create directories
mkdir -p ui api database data

# Create package markers
touch ui/__init__.py api/__init__.py database/__init__.py

# Install dependencies
pip install -r requirements.txt

# Run application
python main.py
```

## Dependencies

```bash
PyQt6>=6.5.0
requests>=2.28.0
```

## Usage

### Chat Interface

1. Select model from dropdown
2. Type message and press **Send**
3. Toggle streaming mode with checkbox

### Model Parameters

- **Creative Mode:** Temperature: `0.8`, Top P: `0.9`
- **Factual Mode:** Temperature: `0.2`, Top P: `0.6`

### Images

1. Click **"Add Image"**
2. Select file
3. Send question about the image

### Conversation Management

- **View history:** `File → Conversation History (Ctrl+H)`
- **New chat:** `File → New Chat (Ctrl+N)`
- **Save:** `File → Save Chat (Ctrl+S)`

## Troubleshooting

If connection errors occur, ensure Ollama is running:

```bash
ollama serve
```

If models are missing, pull them first:

```bash
ollama pull llama3
```

