import sys
import shutil
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QDialog, QVBoxLayout, QHBoxLayout,
                            QLabel, QLineEdit, QPushButton, QMessageBox,
                            QFrame)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QPalette, QColor
from data_manager import DataManager
from main_window import MainWindow

class LoginDialog(QDialog):
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.setup_ui()
        self.setup_styles()

    def setup_styles(self):
        self.setStyleSheet("""
            QDialog {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #232526, stop:1 #414345);
            }
            QLabel {
                color: #E0E0E0;
                font-size: 12px;
            }
            QLineEdit {
                border: 2px solid #424242;
                border-radius: 6px;
                padding: 8px;
                background-color: rgba(45, 45, 45, 0.8);
                color: white;
                min-height: 36px;
                font-size: 12px;
            }
            QLineEdit:focus {
                border: 2px solid #21D4FD;
                background-color: rgba(45, 45, 45, 0.9);
            }
            QPushButton {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #21D4FD, stop:1 #B721FF);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1E90FF, stop:1 #A020F0);
            }
            QPushButton:pressed {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1E90FF, stop:1 #8A2BE2);
            }
            QMessageBox {
                background-color: #2D2D2D;
                color: white;
            }
            QMessageBox QLabel {
                color: white;
            }
        """)

    def setup_ui(self):
        self.setWindowTitle("Digital Safe - Login")
        self.setFixedSize(400, 500)
        self.setWindowFlags(Qt.WindowType.WindowCloseButtonHint)

        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Title and Logo
        title_container = QFrame()
        title_container.setStyleSheet("""
            QFrame {
                background: rgba(45, 45, 45, 0.3);
                border-radius: 12px;
                padding: 16px;
            }
        """)
        title_layout = QVBoxLayout(title_container)
        title_layout.setSpacing(8)

        title = QLabel("Digital Safe")
        title.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        title.setStyleSheet("""
            QLabel {
                color: #21D4FD;
                font-size: 24px;
                font-weight: bold;
            }
        """)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(title)

        subtitle = QLabel("Secure Password & File Manager")
        subtitle.setFont(QFont("Segoe UI", 12))
        subtitle.setStyleSheet("color: #E0E0E0;")
        subtitle.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_layout.addWidget(subtitle)

        layout.addWidget(title_container)

        # Container
        container = QFrame()
        container.setStyleSheet("""
            QFrame {
                background: rgba(45, 45, 45, 0.3);
                border-radius: 12px;
                padding: 16px;
            }
        """)
        container_layout = QVBoxLayout(container)
        container_layout.setSpacing(12)

        # Password input
        password_label = QLabel("Master Password")
        password_label.setFont(QFont("Segoe UI", 11, QFont.Weight.Medium))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_input.setPlaceholderText("Enter your master password")
        self.password_input.returnPressed.connect(self.verify_password)
        container_layout.addWidget(password_label)
        container_layout.addWidget(self.password_input)

        # Login button
        login_button = QPushButton("Login")
        login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        login_button.setFixedHeight(40)
        login_button.clicked.connect(self.verify_password)
        container_layout.addWidget(login_button)

        # Reset button
        reset_button = QPushButton("Reset Digital Safe")
        reset_button.setCursor(Qt.CursorShape.PointingHandCursor)
        reset_button.setFixedHeight(40)
        reset_button.setStyleSheet("""
            QPushButton {
                background: rgba(244, 67, 54, 0.8);
                color: white;
                border: none;
                border-radius: 6px;
                padding: 8px 16px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background: rgba(244, 67, 54, 0.9);
            }
            QPushButton:pressed {
                background: rgba(244, 67, 54, 1);
            }
        """)
        reset_button.clicked.connect(self.reset_safe)
        container_layout.addWidget(reset_button)

        layout.addWidget(container)
        layout.addStretch()

    def reset_safe(self):
        """Reset the Digital Safe by deleting all data."""
        reply = QMessageBox.question(
            self,
            "Reset Digital Safe",
            "Are you sure you want to reset the Digital Safe? This will delete all stored passwords and files.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Delete the .digital_safe directory
                safe_dir = Path.home() / '.digital_safe'
                if safe_dir.exists():
                    shutil.rmtree(safe_dir)
                
                QMessageBox.information(
                    self,
                    "Reset Complete",
                    "Digital Safe has been reset. Please restart the application."
                )
                self.reject()
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Failed to reset Digital Safe: {str(e)}"
                )

    def verify_password(self):
        password = self.password_input.text()
        if not password:
            QMessageBox.warning(self, "Error", "Please enter a password")
            return

        if self.data_manager.is_first_run():
            # First time setup - confirm password
            confirm_dialog = QDialog(self)
            confirm_dialog.setWindowTitle("Confirm Password")
            confirm_dialog.setStyleSheet(self.styleSheet())
            confirm_dialog.setFixedSize(400, 200)
            
            confirm_layout = QVBoxLayout(confirm_dialog)
            confirm_layout.setSpacing(20)
            confirm_layout.setContentsMargins(30, 30, 30, 30)
            
            confirm_label = QLabel("Confirm your master password:")
            confirm_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Medium))
            confirm_input = QLineEdit()
            confirm_input.setEchoMode(QLineEdit.EchoMode.Password)
            confirm_input.setPlaceholderText("Re-enter your master password")
            confirm_button = QPushButton("Confirm")
            
            confirm_layout.addWidget(confirm_label)
            confirm_layout.addWidget(confirm_input)
            confirm_layout.addWidget(confirm_button)
            
            def on_confirm():
                if confirm_input.text() == password:
                    self.data_manager.set_master_password(password)
                    confirm_dialog.accept()
                    self.accept()
                else:
                    QMessageBox.warning(confirm_dialog, "Error", "Passwords do not match")
            
            confirm_button.clicked.connect(on_confirm)
            confirm_input.returnPressed.connect(on_confirm)
            
            if confirm_dialog.exec() == QDialog.DialogCode.Accepted:
                return
        else:
            # Normal login
            if self.data_manager.verify_master_password(password):
                self.accept()
            else:
                QMessageBox.warning(self, "Error", "Invalid password")

def main():
    app = QApplication(sys.argv)
    
    # Set application-wide font
    font = QFont("Segoe UI", 10)
    app.setFont(font)
    
    # Initialize data manager
    data_manager = DataManager()
    
    # Show login dialog
    login_dialog = LoginDialog(data_manager)
    if login_dialog.exec() == QDialog.DialogCode.Accepted:
        # Create and show main window
        window = MainWindow(data_manager)
        window.show()
        sys.exit(app.exec())

if __name__ == "__main__":
    main() 