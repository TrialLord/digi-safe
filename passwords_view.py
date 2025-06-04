from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QMessageBox, QFrame, QTextEdit
from PyQt6.QtGui import QFont, QColor, QIcon
from PyQt6.QtCore import Qt
import string
import random

class PasswordsWidget(QWidget):
    def __init__(self, data_manager, parent=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.setup_ui()
        self.load_data()

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header
        header = QLabel("Passwords")
        header.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        header.setStyleSheet("color: #E0E0E0;")
        layout.addWidget(header)

        # Search bar
        search_container = QFrame()
        search_container.setStyleSheet("""
            QFrame {
                background: rgba(45, 45, 45, 0.3);
                border-radius: 12px;
                padding: 16px;
            }
        """)
        search_layout = QHBoxLayout(search_container)
        search_layout.setContentsMargins(0, 0, 0, 0)
        search_layout.setSpacing(12)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Search passwords...")
        self.search_input.textChanged.connect(self.filter_entries)
        search_layout.addWidget(self.search_input)

        add_btn = QPushButton("Add Password")
        add_btn.setIcon(QIcon("icons/add.svg"))
        add_btn.clicked.connect(self.show_add_dialog)
        search_layout.addWidget(add_btn)

        layout.addWidget(search_container)

        # Entries table
        self.entries_table = QTableWidget()
        self.entries_table.setColumnCount(4)
        self.entries_table.setHorizontalHeaderLabels(["Name", "Username", "Password", "Actions"])
        self.entries_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.entries_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.entries_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch)
        self.entries_table.horizontalHeader().setSectionResizeMode(3, QHeaderView.ResizeMode.Fixed)
        self.entries_table.horizontalHeader().setFixedHeight(40)
        self.entries_table.setStyleSheet("""
            QTableWidget {
                background: rgba(45, 45, 45, 0.3);
                border: none;
                border-radius: 12px;
                gridline-color: rgba(255, 255, 255, 0.1);
            }
            QTableWidget::item {
                padding: 8px;
                color: #E0E0E0;
            }
            QHeaderView::section {
                background: rgba(45, 45, 45, 0.5);
                color: #E0E0E0;
                border: none;
                padding: 8px;
                font-weight: bold;
            }
        """)
        layout.addWidget(self.entries_table)

    def load_data(self):
        """Load password entries from DataManager"""
        self.entries_table.setRowCount(0)
        entries = self.data_manager.get_all_entries()
        
        for name, data in entries.items():
            if data['type'] == 'password':
                row = self.entries_table.rowCount()
                self.entries_table.insertRow(row)
                
                # Name
                name_item = QTableWidgetItem(name)
                name_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
                self.entries_table.setItem(row, 0, name_item)
                
                # Username
                username_item = QTableWidgetItem(data.get('username', ''))
                self.entries_table.setItem(row, 1, username_item)
                
                # Password (hidden)
                password_item = QTableWidgetItem("********")
                password_item.setData(Qt.ItemDataRole.UserRole, data.get('password', ''))
                self.entries_table.setItem(row, 2, password_item)
                
                # Actions
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(4, 4, 4, 4)
                actions_layout.setSpacing(8)
                
                show_btn = QPushButton()
                show_btn.setIcon(QIcon("icons/show.svg"))
                show_btn.setFixedSize(32, 32)
                show_btn.clicked.connect(lambda checked, r=row: self.toggle_password_visibility(r))
                actions_layout.addWidget(show_btn)
                
                delete_btn = QPushButton()
                delete_btn.setIcon(QIcon("icons/delete.svg"))
                delete_btn.setFixedSize(32, 32)
                delete_btn.clicked.connect(lambda checked, n=name: self.delete_entry(n))
                actions_layout.addWidget(delete_btn)
                
                actions_layout.addStretch()
                self.entries_table.setCellWidget(row, 3, actions_widget)
                
                # Set row height
                self.entries_table.setRowHeight(row, 48)

    def toggle_password_visibility(self, row):
        """Toggle password visibility for a row"""
        item = self.entries_table.item(row, 2)
        if item.text() == "********":
            item.setText(item.data(Qt.ItemDataRole.UserRole))
        else:
            item.setText("********")

    def delete_entry(self, name):
        """Delete a password entry"""
        reply = QMessageBox.question(
            self,
            "Confirm Delete",
            f"Are you sure you want to delete '{name}'?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.data_manager.delete_entry(name)
                self.load_data()
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Failed to delete entry: {str(e)}"
                )

    def filter_entries(self):
        """Filter entries based on search text"""
        search_text = self.search_input.text().lower()
        for row in range(self.entries_table.rowCount()):
            name = self.entries_table.item(row, 0).text().lower()
            username = self.entries_table.item(row, 1).text().lower()
            show = search_text in name or search_text in username
            self.entries_table.setRowHidden(row, not show)

    def show_add_dialog(self):
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

    def save_entry(self, dialog, name, username, password, notes):
        """Save a new password entry"""
        if not name or not password:
            QMessageBox.warning(dialog, "Error", "Name and password are required")
            return

        try:
            self.data_manager.add_password(name, username, password, notes)
            self.load_data()
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