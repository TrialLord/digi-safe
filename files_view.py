from PyQt6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QLineEdit, QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox, QFrame
from PyQt6.QtGui import QFont, QColor, QIcon
from PyQt6.QtCore import Qt
import os

class FilesWidget(QWidget):
    def __init__(self, data_manager):
        super().__init__()
        self.data_manager = data_manager
        self.setup_ui()
        self.load_data()  # Load data after UI setup

    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 24, 24, 24)
        layout.setSpacing(16)

        # Header
        header = QLabel("Files")
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
        self.search_input.setPlaceholderText("Search files...")
        self.search_input.textChanged.connect(self.filter_entries)
        search_layout.addWidget(self.search_input)

        add_btn = QPushButton("Add File")
        add_btn.setIcon(QIcon("icons/add.svg"))
        add_btn.clicked.connect(self.show_add_file_dialog)
        search_layout.addWidget(add_btn)

        layout.addWidget(search_container)

        # Files table
        self.files_table = QTableWidget()
        self.files_table.setColumnCount(3)
        self.files_table.setHorizontalHeaderLabels(["Name", "Size", "Actions"])
        self.files_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.files_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Fixed)
        self.files_table.horizontalHeader().setSectionResizeMode(2, QHeaderView.ResizeMode.Fixed)
        self.files_table.horizontalHeader().setFixedHeight(40)
        self.files_table.setStyleSheet("""
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
        layout.addWidget(self.files_table)

    def load_data(self):
        """Load file entries from DataManager"""
        self.files_table.setRowCount(0)
        entries = self.data_manager.get_all_entries()
        
        for name, data in entries.items():
            if data['type'] == 'file':
                row = self.files_table.rowCount()
                self.files_table.insertRow(row)
                
                # Name
                name_item = QTableWidgetItem(name)
                name_item.setFont(QFont("Segoe UI", 10, QFont.Weight.Medium))
                self.files_table.setItem(row, 0, name_item)
                
                # Size
                size = data.get('size', 0)
                size_str = self.format_size(size)
                size_item = QTableWidgetItem(size_str)
                self.files_table.setItem(row, 1, size_item)
                
                # Actions
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(4, 4, 4, 4)
                actions_layout.setSpacing(8)
                
                download_btn = QPushButton()
                download_btn.setIcon(QIcon("icons/download.svg"))
                download_btn.setFixedSize(32, 32)
                download_btn.clicked.connect(lambda checked, n=name: self.download_file(n))
                actions_layout.addWidget(download_btn)
                
                delete_btn = QPushButton()
                delete_btn.setIcon(QIcon("icons/delete.svg"))
                delete_btn.setFixedSize(32, 32)
                delete_btn.clicked.connect(lambda checked, n=name: self.delete_file(n))
                actions_layout.addWidget(delete_btn)
                
                actions_layout.addStretch()
                self.files_table.setCellWidget(row, 2, actions_widget)
                
                # Set row height
                self.files_table.setRowHeight(row, 48)

    def format_size(self, size_bytes):
        """Format file size in human-readable format"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024
        return f"{size_bytes:.1f} TB"

    def download_file(self, name):
        """Download a file"""
        try:
            output_path, _ = QFileDialog.getSaveFileName(
                self,
                "Save File",
                name,
                "All Files (*.*)"
            )
            
            if output_path:
                self.data_manager.get_file(name, output_path)
                QMessageBox.information(
                    self,
                    "Success",
                    "File downloaded successfully!"
                )
        except Exception as e:
            QMessageBox.warning(
                self,
                "Error",
                f"Failed to download file: {str(e)}"
            )

    def delete_file(self, name):
        """Delete a file entry"""
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
                    f"Failed to delete file: {str(e)}"
                )

    def filter_entries(self):
        """Filter entries based on search text"""
        search_text = self.search_input.text().lower()
        for row in range(self.files_table.rowCount()):
            name = self.files_table.item(row, 0).text().lower()
            show = search_text in name
            self.files_table.setRowHidden(row, not show)

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
                self.load_data()
                
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