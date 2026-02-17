"""Custom widgets for Max GUI."""

import logging
from datetime import datetime

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QTextEdit, QGroupBox, QFrame,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QTextCursor, QColor

logger = logging.getLogger(__name__)


class ConversationPanel(QGroupBox):
    """Left panel — displays conversation history."""

    def __init__(self, parent=None):
        super().__init__("Conversation", parent)
        layout = QVBoxLayout()

        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setPlaceholderText("Say 'Max' to start a conversation...")
        layout.addWidget(self.text_area)
        self.setLayout(layout)

    def add_user_message(self, text: str):
        """Add a user message to the conversation."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        html = (
            f'<div style="margin: 4px 0;">'
            f'<span style="color: #888;">[{timestamp}]</span> '
            f'<span style="color: #00ff88; font-weight: bold;">You:</span> '
            f'<span style="color: #e0e0e0;">{text}</span>'
            f'</div>'
        )
        self.text_area.append(html)
        self._scroll_to_bottom()

    def add_max_message(self, text: str):
        """Add a Max response to the conversation."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        html = (
            f'<div style="margin: 4px 0;">'
            f'<span style="color: #888;">[{timestamp}]</span> '
            f'<span style="color: #00d4ff; font-weight: bold;">Max:</span> '
            f'<span style="color: #c8c8d8;">{text}</span>'
            f'</div>'
        )
        self.text_area.append(html)
        self._scroll_to_bottom()

    def add_system_message(self, text: str):
        """Add a system message."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        html = (
            f'<div style="margin: 4px 0;">'
            f'<span style="color: #888;">[{timestamp}]</span> '
            f'<span style="color: #ffaa00;">⚙ {text}</span>'
            f'</div>'
        )
        self.text_area.append(html)
        self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        cursor = self.text_area.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.text_area.setTextCursor(cursor)


class ActionLogPanel(QGroupBox):
    """Right panel — displays action execution logs."""

    def __init__(self, parent=None):
        super().__init__("Action Log", parent)
        layout = QVBoxLayout()

        self.text_area = QTextEdit()
        self.text_area.setReadOnly(True)
        self.text_area.setPlaceholderText("Action execution logs will appear here...")
        layout.addWidget(self.text_area)
        self.setLayout(layout)

    def add_plan(self, plan_json: str):
        """Show the AI's action plan."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        escaped = plan_json.replace("<", "&lt;").replace(">", "&gt;")
        html = (
            f'<div style="margin: 4px 0;">'
            f'<span style="color: #888;">[{timestamp}]</span> '
            f'<span style="color: #aa88ff; font-weight: bold;">PLAN:</span><br>'
            f'<pre style="color: #c8c8d8; margin: 2px 0 2px 16px; font-size: 11px;">{escaped}</pre>'
            f'</div>'
        )
        self.text_area.append(html)
        self._scroll_to_bottom()

    def add_result(self, action_type: str, success: bool, message: str):
        """Show an action execution result."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        color = "#00ff88" if success else "#ff4444"
        icon = "✓" if success else "✗"
        html = (
            f'<div style="margin: 2px 0;">'
            f'<span style="color: #888;">[{timestamp}]</span> '
            f'<span style="color: {color};">{icon}</span> '
            f'<span style="color: #e0e0e0;">{action_type}:</span> '
            f'<span style="color: {color};">{message}</span>'
            f'</div>'
        )
        self.text_area.append(html)
        self._scroll_to_bottom()

    def _scroll_to_bottom(self):
        cursor = self.text_area.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        self.text_area.setTextCursor(cursor)


class StatusBar(QFrame):
    """Bottom status bar with listening indicator and controls."""

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QHBoxLayout()
        layout.setContentsMargins(8, 4, 8, 4)

        # Listening status
        self.status_label = QLabel("● IDLE")
        self.status_label.setObjectName("status_label")
        self.status_label.setProperty("status", "idle")
        layout.addWidget(self.status_label)

        layout.addStretch()

        # Internet indicator
        self.internet_label = QLabel("🌐 Online")
        self.internet_label.setStyleSheet("color: #00ff88;")
        layout.addWidget(self.internet_label)

        # Memory indicator
        self.memory_label = QLabel("💾 0 memories")
        self.memory_label.setStyleSheet("color: #888;")
        layout.addWidget(self.memory_label)

        self.setLayout(layout)

    def set_status(self, status: str, text: str = ""):
        """Update the status indicator.
        
        Args:
            status: One of: idle, listening, processing, executing, error
            text: Optional custom status text
        """
        status_texts = {
            "idle": "● IDLE — Say 'Max' to activate",
            "listening": "🎤 LISTENING...",
            "processing": "🧠 PROCESSING...",
            "executing": "⚡ EXECUTING...",
            "error": "❌ ERROR",
        }
        display_text = text or status_texts.get(status, status)
        self.status_label.setText(display_text)
        self.status_label.setProperty("status", status)
        # Force style refresh
        self.status_label.style().unpolish(self.status_label)
        self.status_label.style().polish(self.status_label)

    def set_internet_status(self, online: bool):
        """Update internet indicator."""
        if online:
            self.internet_label.setText("🌐 Online")
            self.internet_label.setStyleSheet("color: #00ff88;")
        else:
            self.internet_label.setText("🌐 Offline")
            self.internet_label.setStyleSheet("color: #ff4444;")

    def set_memory_count(self, count: int):
        """Update memory count display."""
        self.memory_label.setText(f"💾 {count} memories")
