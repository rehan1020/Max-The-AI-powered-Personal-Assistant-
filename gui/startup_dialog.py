"""Startup validation dialog for Max AI Agent.

Shows a checklist of system requirements on startup.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QScrollArea, QWidget, QListWidget, QListWidgetItem
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QColor, QFont


class StartupDialog(QDialog):
    """Dialog showing startup validation results."""

    def __init__(self, results, parent=None):
        """Initialize the dialog.
        
        Args:
            results: List of CheckResult objects.
            parent: Parent widget.
        """
        super().__init__(parent)
        self.results = results
        self._init_ui()

    def _init_ui(self):
        """Initialize the UI components."""
        self.setWindowTitle("Max AI Agent — Startup Check")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout()
        
        title = QLabel("Startup Validation")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        layout.addWidget(title)
        
        layout.addWidget(QLabel("Checking system requirements..."))
        
        self.status_list = QListWidget()
        for result in self.results:
            item = QListWidgetItem()
            item.setText(f"{'✓' if result.passed else '✗'} {result.name}: {result.message}")
            if result.passed:
                item.setForeground(QColor("#00ff88"))
            else:
                item.setForeground(QColor("#ff4444"))
            self.status_list.addItem(item)
        layout.addWidget(self.status_list)
        
        button_layout = QHBoxLayout()
        
        self.continue_btn = QPushButton("Continue")
        self.continue_btn.clicked.connect(self.accept)
        button_layout.addWidget(self.continue_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
