import json
import requests
from PyQt6.QtCore import QThread, pyqtSignal

class OllamaWorker(QThread):
    """Worker thread for handling Ollama API requests"""
    token_received = pyqtSignal(str)
    response_complete = pyqtSignal(str)
    error_occurred = pyqtSignal(str)
    progress_update = pyqtSignal(int)  # For progress updates
    
    def __init__(self, model, prompt, conversation, params=None, image_data=None, base_url="http://localhost:11434"):
        super().__init__()
        self.model = model
        self.prompt = prompt
        self.conversation = conversation
        self.image_data = image_data
        self.full_response = ""
        self.params = params or {}
        self.token_count = 0
        self.base_url = base_url
        
    def run(self):
        try:
            # Prepare the current message
            current_message = {"role": "user", "content": self.prompt}
            
            # Add image if available
            if self.image_data:
                current_message["images"] = [self.image_data]
                
            # Add to conversation history
            conversation_copy = self.conversation.copy()
            conversation_copy.append(current_message)
            
            # Create the payload with parameters
            payload = {
                "model": self.model,
                "messages": conversation_copy,
                "stream": True  # Enable streaming responses
            }
            
            # Add optional parameters if provided
            for param, value in self.params.items():
                payload[param] = value
                
            # Configure API endpoint
            api_endpoint = f"{self.base_url}/api/chat"
            
            # Make the API call with streaming
            with requests.post(api_endpoint, json=payload, stream=True) as response:
                if response.status_code == 200:
                    # Process the streaming response
                    for line in response.iter_lines():
                        if line:
                            try:
                                # Parse JSON from the line
                                chunk = json.loads(line.decode('utf-8'))
                                
                                # Check if we received a token/response piece
                                if "message" in chunk and "content" in chunk["message"]:
                                    token = chunk["message"]["content"]
                                    self.full_response += token
                                    self.token_count += 1
                                    self.token_received.emit(token)
                                    
                                # Alternative format - direct "response" field
                                elif "response" in chunk:
                                    token = chunk["response"]
                                    self.full_response += token
                                    self.token_count += 1
                                    self.token_received.emit(token)
                                    
                                # Update progress (assuming max_tokens parameter is used)
                                max_tokens = self.params.get("max_tokens", 2048)
                                progress = min(100, int((self.token_count / max_tokens) * 100))
                                self.progress_update.emit(progress)
                                    
                                # Check if we're done
                                if chunk.get("done", False):
                                    self.response_complete.emit(self.full_response)
                                    self.progress_update.emit(100)  # Ensure progress bar completes
                                    break
                            except json.JSONDecodeError:
                                continue
                else:
                    self.error_occurred.emit(f"Error: {response.status_code} - {response.text}")
                
        except Exception as e:
            self.error_occurred.emit(f"Error: {str(e)}")

    def get_models(self):
        """Get available models from Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                return [model['name'] for model in response.json()['models']]
            return []
        except Exception:
            return []