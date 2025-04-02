import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QIcon, QFont

from ui.main_window import OllamaChatUI
from ui.theme import apply_default_theme

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Remove this section or make it a try-except that doesn't exit on failure
    # The default system fonts will be used instead
    """
    font_id = QFontDatabase.addApplicationFont("fonts/Roboto-Regular.ttf")
    if font_id >= 0:
        font_family = QFontDatabase.applicationFontFamilies(font_id)[0]
        app.setFont(QFont(font_family, 10))
    """
    
    # Just use system font directly
    app.setFont(QFont("Segoe UI", 10))
    
    # Set application icon - this needs to exist too
    # Comment out if the icon file doesn't exist
    # app.setWindowIcon(QIcon("icons/app_icon.png"))
    
    # Set application style
    apply_default_theme(app)
    
    window = OllamaChatUI()
    window.show()
    
    sys.exit(app.exec())