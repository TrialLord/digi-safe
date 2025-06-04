from PyQt6.QtWidgets import QWidget, QVBoxLayout, QLabel, QPushButton, QHBoxLayout, QFrame, QDialog, QGridLayout, QLineEdit, QTextEdit, QFileDialog, QMessageBox
from PyQt6.QtGui import QFont, QColor, QIcon
from PyQt6.QtCore import Qt
import os
import string
import random

class DashboardWidget(QWidget):
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.setup_ui()
        self.refresh_summary()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(24)
        layout.setContentsMargins(40, 40, 40, 40)

        # Welcome
        welcome = QLabel("Welcome to Digital Safe!")
        welcome.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        welcome.setStyleSheet("color: #21D4FD;")
        layout.addWidget(welcome)

        # Summary
        self.summary_frame = QFrame()
        self.summary_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #232526, stop:1 #414345);
                border-radius: 16px;
                padding: 24px;
                box-shadow: 0 4px 24px rgba(33,212,253,0.12);
            }
        """)
        self.summary_layout = QHBoxLayout(self.summary_frame)
        self.summary_layout.setSpacing(40)

        # Create labels for summary
        self.passwords_label = QLabel()
        self.passwords_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.passwords_label.setStyleSheet("color: #21D4FD; font-size: 20px;")
        
        self.files_label = QLabel()
        self.files_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.files_label.setStyleSheet("color: #B721FF; font-size: 20px;")
        
        self.summary_layout.addWidget(self.passwords_label)
        self.summary_layout.addWidget(self.files_label)

        layout.addWidget(self.summary_frame)

        # Quick Actions
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(20)
        add_password_btn = QPushButton("Add Password")
        add_password_btn.setStyleSheet("background-color: #21D4FD; color: #232526; border-radius: 8px; padding: 12px 32px; font-weight: bold;")
        add_password_btn.clicked.connect(self.show_add_password_dialog)
        
        add_file_btn = QPushButton("Add File")
        add_file_btn.setStyleSheet("background-color: #B721FF; color: #fff; border-radius: 8px; padding: 12px 32px; font-weight: bold;")
        add_file_btn.clicked.connect(self.show_add_file_dialog)
        
        lock_btn = QPushButton("Lock Safe")
        lock_btn.setStyleSheet("background-color: #232526; color: #fff; border-radius: 8px; padding: 12px 32px; font-weight: bold; border: 2px solid #21D4FD;")
        lock_btn.clicked.connect(self.lock_safe)
        
        actions_layout.addWidget(add_password_btn)
        actions_layout.addWidget(add_file_btn)
        actions_layout.addWidget(lock_btn)
        layout.addLayout(actions_layout)

        layout.addStretch()

        # Expose buttons for main window to connect
        self.add_password_btn = add_password_btn
        self.add_file_btn = add_file_btn
        self.lock_btn = lock_btn

    def refresh_summary(self):
        """Refresh the summary counts"""
        entries = self.data_manager.get_all_entries()
        num_passwords = sum(1 for e in entries.values() if e['type'] == 'password')
        num_files = sum(1 for e in entries.values() if e['type'] == 'file')
        
        self.passwords_label.setText(f"<b>{num_passwords}</b><br>Passwords")
        self.files_label.setText(f"<b>{num_files}</b><br>Files")

    def show_add_password_dialog(self):
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
                
                # Refresh summary
                self.refresh_summary()
                
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
            self.data_manager.add_password(name, username, password, notes)
            # Refresh summary
            self.refresh_summary()
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

    def lock_safe(self):
        """Lock the safe and return to login screen"""
        self.window().close() 