import sys
import os
import pyperclip
import string
import random
from PyQt6.QtWidgets import QMainWindow, QWidget, QVBoxLayout, QHBoxLayout
from PyQt6.QtWidgets import QPushButton, QLineEdit, QLabel, QTableWidget, QTableWidgetItem
from PyQt6.QtWidgets import QMessageBox, QDialog, QSpinBox, QCheckBox, QMenu, QMenuBar
from PyQt6.QtWidgets import QFileDialog, QFrame, QStyleFactory, QApplication
from PyQt6.QtWidgets import QListWidget, QListWidgetItem, QStackedWidget
from PyQt6.QtCore import Qt, QTimer, QSize, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QAction, QIcon, QPalette, QColor, QFont, QFontDatabase
from data_manager import DataManager
from crypto import CryptoManager
from dashboard import DashboardWidget
from passwords_view import PasswordsWidget
from files_view import FilesWidget
from settings_view import SettingsWidget

class PasswordGeneratorDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Generate Password")
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        
        # Length control
        length_layout = QHBoxLayout()
        length_layout.addWidget(QLabel("Length:"))
        self.length_spin = QSpinBox()
        self.length_spin.setRange(8, 64)
        self.length_spin.setValue(16)
        length_layout.addWidget(self.length_spin)
        layout.addLayout(length_layout)

        # Symbols checkbox
        self.symbols_check = QCheckBox("Include Symbols")
        self.symbols_check.setChecked(True)
        layout.addWidget(self.symbols_check)

        # Generated password
        self.password_edit = QLineEdit()
        self.password_edit.setReadOnly(True)
        layout.addWidget(self.password_edit)

        # Buttons
        button_layout = QHBoxLayout()
        generate_btn = QPushButton("Generate")
        generate_btn.clicked.connect(self.generate_password)
        copy_btn = QPushButton("Copy")
        copy_btn.clicked.connect(self.copy_password)
        button_layout.addWidget(generate_btn)
        button_layout.addWidget(copy_btn)
        layout.addLayout(button_layout)

        self.setLayout(layout)
        self.generate_password()

    def generate_password(self):
        crypto = CryptoManager()
        password = crypto.generate_password(
            self.length_spin.value(),
            self.symbols_check.isChecked()
        )
        self.password_edit.setText(password)

    def copy_password(self):
        pyperclip.copy(self.password_edit.text())
        QMessageBox.information(self, "Success", "Password copied to clipboard!")

class StyledButton(QPushButton):
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setMinimumHeight(40)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        self.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
            QPushButton:pressed {
                background-color: #1565C0;
            }
            QPushButton:disabled {
                background-color: #424242;
            }
        """)

class StyledLineEdit(QLineEdit):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setMinimumHeight(40)
        self.setStyleSheet("""
            QLineEdit {
                border: 2px solid #424242;
                border-radius: 4px;
                padding: 8px;
                background-color: #2D2D2D;
                color: white;
            }
            QLineEdit:focus {
                border: 2px solid #2196F3;
            }
        """)

class StyledTableWidget(QTableWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet("""
            QTableWidget {
                border: none;
                background-color: #1E1E1E;
                color: white;
                gridline-color: #424242;
            }
            QTableWidget::item {
                padding: 8px;
                border-bottom: 1px solid #424242;
            }
            QTableWidget::item:selected {
                background-color: #2D2D2D;
                color: white;
            }
            QHeaderView::section {
                background-color: #2D2D2D;
                padding: 8px;
                border: none;
                border-bottom: 2px solid #424242;
                font-weight: bold;
                color: white;
            }
        """)
        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        self.verticalHeader().setVisible(False)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

class MainWindow(QMainWindow):
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.clipboard_timer = QTimer()
        self.clipboard_timer.timeout.connect(self.clear_clipboard)
        self.setup_ui()
        self.load_data()
        self.setup_styles()

    def setup_ui(self):
        self.setWindowTitle("Digital Safe")
        self.setMinimumSize(1200, 800)
        self.setStyleSheet("""
            QMainWindow {
                background: #1E1E1E;
            }
            QWidget {
                color: #E0E0E0;
            }
        """)

        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Create sidebar
        sidebar = QFrame()
        sidebar.setFixedWidth(240)
        sidebar.setStyleSheet("""
            QFrame {
                background: #2D2D2D;
                border-right: 1px solid #3D3D3D;
            }
            QPushButton {
                text-align: left;
                padding: 12px 24px;
                border: none;
                color: #E0E0E0;
                font-size: 14px;
                font-weight: 500;
            }
            QPushButton:hover {
                background: #3D3D3D;
            }
            QPushButton:checked {
                background: #3D3D3D;
                border-left: 4px solid #21D4FD;
            }
        """)
        sidebar_layout = QVBoxLayout(sidebar)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)

        # Create navigation buttons
        self.nav_buttons = []
        nav_items = [
            ("Dashboard", "icons/dashboard.svg"),
            ("Passwords", "icons/passwords.svg"),
            ("Files", "icons/files.svg"),
            ("Settings", "icons/settings.svg")
        ]

        for text, icon_path in nav_items:
            btn = QPushButton(text)
            btn.setCheckable(True)
            btn.setIcon(QIcon(icon_path))
            btn.setIconSize(QSize(20, 20))
            btn.clicked.connect(lambda checked, t=text: self.switch_view(t))
            sidebar_layout.addWidget(btn)
            self.nav_buttons.append(btn)

        sidebar_layout.addStretch()
        main_layout.addWidget(sidebar)

        # Create stack widget for different views
        self.stack = QStackedWidget()
        self.stack.setStyleSheet("""
            QStackedWidget {
                background: #1E1E1E;
            }
        """)

        # Add views to stack
        self.dashboard = DashboardWidget(self.data_manager)
        self.passwords = PasswordsWidget(self.data_manager)
        self.files = FilesWidget(self.data_manager)
        self.settings = SettingsWidget()

        self.stack.addWidget(self.dashboard)
        self.stack.addWidget(self.passwords)
        self.stack.addWidget(self.files)
        self.stack.addWidget(self.settings)

        main_layout.addWidget(self.stack)

        # Set initial view
        self.nav_buttons[0].setChecked(True)
        self.stack.setCurrentWidget(self.dashboard)

    def setup_styles(self):
        font = QFont("Segoe UI", 10)
        QApplication.setFont(font)
        self.setStyleSheet("""
            QMainWindow {
                background-color: #1E1E1E;
            }
            QLabel {
                color: #E0E0E0;
                font-size: 14px;
            }
            QMenuBar {
                background-color: #2D2D2D;
                color: white;
                border-bottom: 1px solid #424242;
            }
            QMenuBar::item {
                padding: 8px 12px;
                color: white;
            }
            QMenuBar::item:selected {
                background-color: #424242;
            }
            QMenu {
                background-color: #2D2D2D;
                color: white;
                border: 1px solid #424242;
            }
            QMenu::item {
                padding: 8px 24px;
                color: white;
            }
            QMenu::item:selected {
                background-color: #424242;
            }
            QMessageBox {
                background-color: #2D2D2D;
                color: white;
            }
            QMessageBox QLabel {
                color: white;
            }
        """)

    def load_data(self):
        """Load data from DataManager"""
        self.passwords.load_data()
        self.files.load_data()

    def switch_view(self, view_name):
        # Update button states
        for btn in self.nav_buttons:
            btn.setChecked(btn.text() == view_name)

        # Switch to corresponding view and refresh data
        if view_name == "Dashboard":
            self.dashboard.refresh_summary()
            self.stack.setCurrentWidget(self.dashboard)
        elif view_name == "Passwords":
            self.passwords.load_data()
            self.stack.setCurrentWidget(self.passwords)
        elif view_name == "Files":
            self.files.load_data()
            self.stack.setCurrentWidget(self.files)
        elif view_name == "Settings":
            self.stack.setCurrentWidget(self.settings)

    def show_add_entry_dialog(self):
        """Show dialog to add a new password entry"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Add Password")
        dialog.setStyleSheet("""
            QDialog {
                background: #2D2D2D;
            }
            QLabel {
                color: #E0E0E0;
                font-size: 12px;
            }
            QLineEdit, QTextEdit {
                border: 2px solid #424242;
                border-radius: 6px;
                padding: 8px;
                background-color: rgba(45, 45, 45, 0.8);
                color: white;
                min-height: 36px;
                font-size: 12px;
            }
            QLineEdit:focus, QTextEdit:focus {
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
        """)
        dialog.setFixedSize(400, 500)

        layout = QVBoxLayout(dialog)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        # Input fields
        name_input = QLineEdit()
        name_input.setPlaceholderText("Name")
        username_input = QLineEdit()
        username_input.setPlaceholderText("Username")
        password_input = QLineEdit()
        password_input.setPlaceholderText("Password")
        password_input.setEchoMode(QLineEdit.EchoMode.Password)
        notes_input = QTextEdit()
        notes_input.setPlaceholderText("Notes")
        notes_input.setMaximumHeight(100)

        # Generate password button
        generate_btn = QPushButton("Generate Password")
        generate_btn.setIcon(QIcon("icons/key.svg"))
        generate_btn.clicked.connect(lambda: password_input.setText(self.generate_password()))

        # Save button
        save_btn = QPushButton("Save")
        save_btn.clicked.connect(lambda: self.save_entry(
            dialog, name_input.text(), username_input.text(),
            password_input.text(), notes_input.toPlainText()
        ))

        # Add widgets to layout
        layout.addWidget(QLabel("Name:"))
        layout.addWidget(name_input)
        layout.addWidget(QLabel("Username:"))
        layout.addWidget(username_input)
        layout.addWidget(QLabel("Password:"))
        layout.addWidget(password_input)
        layout.addWidget(generate_btn)
        layout.addWidget(QLabel("Notes:"))
        layout.addWidget(notes_input)
        layout.addStretch()
        layout.addWidget(save_btn)

        dialog.exec()

    def show_add_file_dialog(self):
        """Show dialog to add a new file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select File",
            "",
            "All Files (*.*)"
        )

        if file_path:
            try:
                # Get file name from path
                file_name = os.path.basename(file_path)
                
                # Add file to DataManager
                self.data_manager.add_file(file_name, file_path)
                
                # Refresh files view
                self.files.load_data()
                
                QMessageBox.information(
                    self,
                    "Success",
                    f"File '{file_name}' added successfully!"
                )
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Failed to add file: {str(e)}"
                )

    def save_entry(self, dialog, name, username, password, notes):
        """Save a new password entry"""
        if not name or not password:
            QMessageBox.warning(dialog, "Error", "Name and password are required")
            return

        try:
            # Add entry to DataManager
            self.data_manager.add_password(name, username, password, notes)
            
            # Refresh passwords view
            self.passwords.load_data()
            
            QMessageBox.information(
                dialog,
                "Success",
                "Password entry added successfully!"
            )
            dialog.accept()
        except Exception as e:
            QMessageBox.warning(
                dialog,
                "Error",
                f"Failed to add password entry: {str(e)}"
            )

    def generate_password(self):
        """Generate a secure random password"""
        length = 16
        chars = string.ascii_letters + string.digits + "!@#$%^&*"
        return ''.join(random.choice(chars) for _ in range(length))

    def clear_clipboard(self):
        pyperclip.copy("")
        self.clipboard_timer.stop()

    def filter_entries(self):
        search_text = self.search_input.text().lower()
        for row in range(self.entries_table.rowCount()):
            name = self.entries_table.item(row, 0).text().lower()
            username = self.entries_table.item(row, 1).text().lower()
            show = search_text in name or search_text in username
            self.entries_table.setRowHidden(row, not show)

    def show_snackbar(self, message):
        QMessageBox.information(self, "Info", message) 