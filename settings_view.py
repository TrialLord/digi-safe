from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QSpinBox, QMessageBox, QApplication
from PyQt6.QtGui import QFont, QColor
from PyQt6.QtCore import Qt

class SettingsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.load_settings()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)

        # Header
        header = QLabel("Settings")
        header.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        header.setStyleSheet("color: #21D4FD;")
        layout.addWidget(header)

        # Theme
        theme_layout = QHBoxLayout()
        theme_layout.addWidget(QLabel("Theme:"))
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Dark", "Light"])
        self.theme_combo.setStyleSheet("""
            QComboBox {
                background-color: #2D2D2D;
                color: #E0E0E0;
                border-radius: 8px;
                padding: 8px;
                min-width: 200px;
            }
            QComboBox::drop-down {
                border: none;
            }
            QComboBox::down-arrow {
                image: url(icons/dropdown.svg);
                width: 12px;
                height: 12px;
            }
        """)
        self.theme_combo.currentTextChanged.connect(self.change_theme)
        theme_layout.addWidget(self.theme_combo)
        layout.addLayout(theme_layout)

        # Font Size
        font_layout = QHBoxLayout()
        font_layout.addWidget(QLabel("Font Size:"))
        self.font_spin = QSpinBox()
        self.font_spin.setRange(8, 24)
        self.font_spin.setValue(10)
        self.font_spin.setStyleSheet("""
            QSpinBox {
                background-color: #2D2D2D;
                color: #E0E0E0;
                border-radius: 8px;
                padding: 8px;
                min-width: 100px;
            }
            QSpinBox::up-button, QSpinBox::down-button {
                width: 20px;
                border: none;
            }
        """)
        self.font_spin.valueChanged.connect(self.change_font_size)
        font_layout.addWidget(self.font_spin)
        layout.addLayout(font_layout)

        # About
        about_btn = QPushButton("About")
        about_btn.setStyleSheet("""
            QPushButton {
                background-color: #21D4FD;
                color: #232526;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #1E90FF;
            }
        """)
        about_btn.clicked.connect(self.show_about)
        layout.addWidget(about_btn)

        layout.addStretch()

    def load_settings(self):
        """Load saved settings"""
        # TODO: Load from config file
        self.theme_combo.setCurrentText("Dark")
        self.font_spin.setValue(10)

    def change_theme(self, theme):
        """Change application theme"""
        if theme == "Dark":
            self.set_dark_theme()
        else:
            self.set_light_theme()

    def set_dark_theme(self):
        """Apply dark theme"""
        app = QApplication.instance()
        app.setStyleSheet("""
            QWidget {
                background-color: #1E1E1E;
                color: #E0E0E0;
            }
            QLabel {
                color: #E0E0E0;
            }
            QPushButton {
                background-color: #21D4FD;
                color: #232526;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1E90FF;
            }
            QLineEdit, QTextEdit {
                background-color: #2D2D2D;
                color: #E0E0E0;
                border: 2px solid #424242;
                border-radius: 8px;
                padding: 8px;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 2px solid #21D4FD;
            }
        """)

    def set_light_theme(self):
        """Apply light theme"""
        app = QApplication.instance()
        app.setStyleSheet("""
            QWidget {
                background-color: #FFFFFF;
                color: #232526;
            }
            QLabel {
                color: #232526;
            }
            QPushButton {
                background-color: #21D4FD;
                color: #FFFFFF;
                border-radius: 8px;
                padding: 12px 24px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1E90FF;
            }
            QLineEdit, QTextEdit {
                background-color: #F5F5F5;
                color: #232526;
                border: 2px solid #E0E0E0;
                border-radius: 8px;
                padding: 8px;
            }
            QLineEdit:focus, QTextEdit:focus {
                border: 2px solid #21D4FD;
            }
        """)

    def change_font_size(self, size):
        """Change application font size"""
        app = QApplication.instance()
        font = QFont("Segoe UI", size)
        app.setFont(font)

    def show_about(self):
        """Show about dialog"""
        QMessageBox.information(
            self,
            "About Digital Safe",
            "Digital Safe v1.0\n\n"
            "A secure password and file manager that helps you keep your sensitive data safe.\n\n"
            "Features:\n"
            "• Secure password storage\n"
            "• File encryption\n"
            "• Password generation\n"
            "• Dark/Light themes\n"
            "• Customizable font size"
        ) 