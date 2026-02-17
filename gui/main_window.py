"""Main window for Max Desktop Agent GUI.

Professional layout:
  - Left panel: Conversation history
  - Right panel: Action log
  - Bottom: Status bar with controls
  - Top: Title + control buttons
"""

import json
import logging
import threading
from typing import Optional

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QSplitter, QCheckBox,
    QMessageBox, QApplication,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QFont

from gui.styles import DARK_THEME
from gui.widgets import ConversationPanel, ActionLogPanel, StatusBar

logger = logging.getLogger(__name__)


class ConfirmationSignal(QWidget):
    """Helper widget to emit signals for thread-safe confirmation dialogs."""
    request_confirmation = pyqtSignal(str)
    

class MaxMainWindow(QMainWindow):
    """Main application window for Max Desktop Agent."""

    # Signals for thread-safe GUI updates from background threads
    sig_user_message = pyqtSignal(str)
    sig_max_message = pyqtSignal(str)
    sig_system_message = pyqtSignal(str)
    sig_add_plan = pyqtSignal(str)
    sig_add_result = pyqtSignal(str, bool, str)
    sig_set_status = pyqtSignal(str, str)
    sig_set_memory_count = pyqtSignal(int)
    sig_request_confirmation = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Max — AI Desktop Agent")
        self.setMinimumSize(1000, 650)
        self.resize(1200, 750)

        self._confirmation_result: Optional[bool] = None
        self._confirmation_event = threading.Event()

        self._setup_ui()
        self._connect_signals()
        self._apply_styles()

        # Callbacks — set by orchestrator
        self.on_start: Optional[callable] = None
        self.on_stop: Optional[callable] = None
        self.on_safe_mode_changed: Optional[callable] = None

    def _setup_ui(self):
        """Build the UI layout."""
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        main_layout.setSpacing(8)
        main_layout.setContentsMargins(12, 8, 12, 8)

        # ── Top Bar ──
        top_bar = QHBoxLayout()

        title = QLabel("🧠 MAX")
        title.setObjectName("title_label")
        top_bar.addWidget(title)

        top_bar.addStretch()

        # Safe mode toggle
        self.safe_mode_cb = QCheckBox("Safe Mode")
        self.safe_mode_cb.setChecked(True)
        self.safe_mode_cb.setToolTip("When enabled, dangerous actions require manual confirmation")
        self.safe_mode_cb.stateChanged.connect(self._on_safe_mode_changed)
        top_bar.addWidget(self.safe_mode_cb)

        # Start button
        self.start_btn = QPushButton("▶ Start Listening")
        self.start_btn.setObjectName("start_btn")
        self.start_btn.setFixedWidth(160)
        self.start_btn.clicked.connect(self._on_start_clicked)
        top_bar.addWidget(self.start_btn)

        # Stop button
        self.stop_btn = QPushButton("■ Stop")
        self.stop_btn.setObjectName("stop_btn")
        self.stop_btn.setFixedWidth(100)
        self.stop_btn.setEnabled(False)
        self.stop_btn.clicked.connect(self._on_stop_clicked)
        top_bar.addWidget(self.stop_btn)

        main_layout.addLayout(top_bar)

        # ── Main Content (Splitter) ──
        splitter = QSplitter(Qt.Orientation.Horizontal)

        self.conversation_panel = ConversationPanel()
        splitter.addWidget(self.conversation_panel)

        self.action_log_panel = ActionLogPanel()
        splitter.addWidget(self.action_log_panel)

        splitter.setSizes([600, 400])
        main_layout.addWidget(splitter, stretch=1)

        # ── Status Bar ──
        self.status_bar = StatusBar()
        main_layout.addWidget(self.status_bar)

    def _connect_signals(self):
        """Connect signals for thread-safe GUI updates."""
        self.sig_user_message.connect(self.conversation_panel.add_user_message)
        self.sig_max_message.connect(self.conversation_panel.add_max_message)
        self.sig_system_message.connect(self.conversation_panel.add_system_message)
        self.sig_add_plan.connect(self.action_log_panel.add_plan)
        self.sig_add_result.connect(self.action_log_panel.add_result)
        self.sig_set_status.connect(self.status_bar.set_status)
        self.sig_set_memory_count.connect(self.status_bar.set_memory_count)
        self.sig_request_confirmation.connect(self._show_confirmation_dialog)

    def _apply_styles(self):
        """Apply the dark theme stylesheet."""
        self.setStyleSheet(DARK_THEME)

    # ── Public Methods (thread-safe via signals) ──

    def add_user_message(self, text: str):
        self.sig_user_message.emit(text)

    def add_max_message(self, text: str):
        self.sig_max_message.emit(text)

    def add_system_message(self, text: str):
        self.sig_system_message.emit(text)

    def add_plan(self, plan_json: str):
        self.sig_add_plan.emit(plan_json)

    def add_result(self, action_type: str, success: bool, message: str):
        self.sig_add_result.emit(action_type, success, message)

    def set_status(self, status: str, text: str = ""):
        self.sig_set_status.emit(status, text)

    def set_memory_count(self, count: int):
        self.sig_set_memory_count.emit(count)

    def request_confirmation(self, message: str) -> bool:
        """Request user confirmation. Thread-safe — blocks until user responds.
        
        Args:
            message: The confirmation message to display.
        
        Returns:
            True if user approved, False otherwise.
        """
        self._confirmation_event.clear()
        self._confirmation_result = None
        self.sig_request_confirmation.emit(message)
        self._confirmation_event.wait(timeout=60)  # 60s timeout
        return self._confirmation_result or False

    # ── Slots ──

    def _show_confirmation_dialog(self, message: str):
        """Show confirmation dialog (must run on GUI thread)."""
        reply = QMessageBox.question(
            self,
            "Max — Action Confirmation Required",
            message,
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No,
        )
        self._confirmation_result = (reply == QMessageBox.StandardButton.Yes)
        self._confirmation_event.set()

    def _on_start_clicked(self):
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.set_status("listening")
        if self.on_start:
            threading.Thread(target=self.on_start, daemon=True).start()

    def _on_stop_clicked(self):
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.set_status("idle")
        if self.on_stop:
            self.on_stop()

    def _on_safe_mode_changed(self, state):
        enabled = state == Qt.CheckState.Checked.value
        if self.on_safe_mode_changed:
            self.on_safe_mode_changed(enabled)

    def closeEvent(self, event):
        """Handle window close."""
        if self.on_stop:
            self.on_stop()
        event.accept()
