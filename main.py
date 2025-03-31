import sys
from PyQt6.QtWidgets import QApplication

from ui.main_window import OllamaChatUI
from ui.theme import apply_default_theme

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Set application style
    apply_default_theme(app)
    
    window = OllamaChatUI()
    window.show()
    
    sys.exit(app.exec())