from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPalette, QColor, QFont

# Dark theme stylesheet
DARK_THEME = """
/* Main Background */
#mainWindow, QWidget {
    background-color: #202123;
    color: #ECECF1;
}

QStatusBar {
    background-color: #343541;
    color: #ECECF1;
    border-top: 1px solid #444654;
}

/* Chat Messages */
#userMessage {
    background-color: #343541;
    color: #ECECF1;
    border-radius: 8px;
    border: 1px solid #444654;
}

#assistantMessage {
    background-color: #444654;
    color: #ECECF1;
    border-radius: 8px;
    border: 1px solid #565869;
}

/* Input Area */
QTextEdit#inputField {
    background-color: #40414f;
    color: #ECECF1;
    border-radius: 8px;
    border: 1px solid #565869;
    padding: 8px;
    selection-background-color: #10a37f;
}

/* Buttons */
QPushButton {
    background-color: #10a37f;
    color: white;
    border-radius: 4px;
    padding: 8px 16px;
    border: none;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #0D8B6C;
}

QPushButton:pressed {
    background-color: #0A725A;
}

QPushButton:disabled {
    background-color: #2A3439;
    color: #6E7681;
}

QPushButton#iconButton {
    background-color: transparent;
    border-radius: 4px;
    padding: 4px;
}

QPushButton#iconButton:hover {
    background-color: rgba(255, 255, 255, 0.1);
}

/* Dropdown & Combobox */
QComboBox {
    background-color: #40414f;
    color: #ECECF1;
    border-radius: 4px;
    padding: 6px;
    border: 1px solid #565869;
}

QComboBox::drop-down {
    border: none;
    padding-right: 10px;
}

QComboBox QAbstractItemView {
    background-color: #40414f;
    color: #ECECF1;
    selection-background-color: #10a37f;
}

/* Scrollbars */
QScrollBar:vertical {
    background-color: #343541;
    width: 10px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background-color: #565869;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background-color: #10a37f;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Checkboxes */
QCheckBox {
    color: #ECECF1;
    spacing: 5px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 3px;
    border: 1px solid #565869;
}

QCheckBox::indicator:checked {
    background-color: #10a37f;
    border: 1px solid #10a37f;
}

/* Sliders */
QSlider::groove:horizontal {
    border: 1px solid #565869;
    height: 6px;
    border-radius: 3px;
    background: #40414f;
}

QSlider::handle:horizontal {
    background: #10a37f;
    border: none;
    width: 18px;
    height: 18px;
    border-radius: 9px;
    margin: -6px 0;
}

QSlider::handle:horizontal:hover {
    background: #0D8B6C;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #565869;
    border-radius: 4px;
    background-color: #343541;
}

QTabBar::tab {
    background-color: #40414f;
    color: #ECECF1;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 8px 16px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #10a37f;
}

QTabBar::tab:hover:!selected {
    background-color: #565869;
}

/* Progress Bar */
QProgressBar {
    border: 1px solid #565869;
    border-radius: 4px;
    text-align: center;
    background-color: #40414f;
}

QProgressBar::chunk {
    background-color: #10a37f;
    border-radius: 3px;
}

/* Labels */
QLabel {
    color: #ECECF1;
}

/* Tooltip */
QToolTip {
    background-color: #343541;
    color: #ECECF1;
    border: 1px solid #565869;
    border-radius: 4px;
    padding: 4px;
}
"""

# Light theme stylesheet
LIGHT_THEME = """
/* Main Background */
#mainWindow, QWidget {
    background-color: #FFFFFF;
    color: #202123;
}

QStatusBar {
    background-color: #F7F7F8;
    color: #202123;
    border-top: 1px solid #E5E5E5;
}

/* Chat Messages */
#userMessage {
    background-color: #F7F7F8;
    color: #202123;
    border-radius: 8px;
    border: 1px solid #E5E5E5;
}

#assistantMessage {
    background-color: #ECECF1;
    color: #202123;
    border-radius: 8px;
    border: 1px solid #D9D9E3;
}

/* Input Area */
QTextEdit#inputField {
    background-color: #FFFFFF;
    color: #202123;
    border-radius: 8px;
    border: 1px solid #D9D9E3;
    padding: 8px;
    selection-background-color: #10a37f;
}

/* Buttons */
QPushButton {
    background-color: #10a37f;
    color: white;
    border-radius: 4px;
    padding: 8px 16px;
    border: none;
    font-weight: bold;
}

QPushButton:hover {
    background-color: #0D8B6C;
}

QPushButton:pressed {
    background-color: #0A725A;
}

QPushButton:disabled {
    background-color: #E5E5E5;
    color: #A0A0A0;
}

QPushButton#iconButton {
    background-color: transparent;
    border-radius: 4px;
    padding: 4px;
}

QPushButton#iconButton:hover {
    background-color: rgba(0, 0, 0, 0.1);
}

/* Dropdown & Combobox */
QComboBox {
    background-color: #FFFFFF;
    color: #202123;
    border-radius: 4px;
    padding: 6px;
    border: 1px solid #D9D9E3;
}

QComboBox::drop-down {
    border: none;
    padding-right: 10px;
}

QComboBox QAbstractItemView {
    background-color: #FFFFFF;
    color: #202123;
    selection-background-color: #10a37f;
}

/* Scrollbars */
QScrollBar:vertical {
    background-color: #F7F7F8;
    width: 10px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background-color: #D9D9E3;
    min-height: 20px;
    border-radius: 5px;
}

QScrollBar::handle:vertical:hover {
    background-color: #10a37f;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

/* Checkboxes */
QCheckBox {
    color: #202123;
    spacing: 5px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border-radius: 3px;
    border: 1px solid #D9D9E3;
}

QCheckBox::indicator:checked {
    background-color: #10a37f;
    border: 1px solid #10a37f;
}

/* Sliders */
QSlider::groove:horizontal {
    border: 1px solid #D9D9E3;
    height: 6px;
    border-radius: 3px;
    background: #F7F7F8;
}

QSlider::handle:horizontal {
    background: #10a37f;
    border: none;
    width: 18px;
    height: 18px;
    border-radius: 9px;
    margin: -6px 0;
}

QSlider::handle:horizontal:hover {
    background: #0D8B6C;
}

/* Tabs */
QTabWidget::pane {
    border: 1px solid #D9D9E3;
    border-radius: 4px;
    background-color: #FFFFFF;
}

QTabBar::tab {
    background-color: #F7F7F8;
    color: #202123;
    border-top-left-radius: 4px;
    border-top-right-radius: 4px;
    padding: 8px 16px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #10a37f;
    color: white;
}

QTabBar::tab:hover:!selected {
    background-color: #ECECF1;
}

/* Progress Bar */
QProgressBar {
    border: 1px solid #D9D9E3;
    border-radius: 4px;
    text-align: center;
    background-color: #F7F7F8;
}

QProgressBar::chunk {
    background-color: #10a37f;
    border-radius: 3px;
}

/* Labels */
QLabel {
    color: #202123;
}

/* Tooltip */
QToolTip {
    background-color: #FFFFFF;
    color: #202123;
    border: 1px solid #D9D9E3;
    border-radius: 4px;
    padding: 4px;
}
"""

def apply_theme(app_or_widget, is_dark_theme=True):
    """Apply the selected theme to the application or widget"""
    if is_dark_theme:
        app_or_widget.setStyleSheet(DARK_THEME)
    else:
        app_or_widget.setStyleSheet(LIGHT_THEME)

def apply_default_theme(app):
    """Apply the default theme (dark)"""
    app.setStyleSheet(DARK_THEME)
    
    # Set default font
    font = QFont("Segoe UI", 10)
    app.setFont(font)