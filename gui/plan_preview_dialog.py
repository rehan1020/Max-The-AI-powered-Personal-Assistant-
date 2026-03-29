"""Plan preview dialog for Max AI Agent.

Shows planned actions before execution for user approval.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
    QPushButton, QTextEdit, QScrollArea, QWidget
)
from PyQt6.QtCore import Qt


class PlanPreviewDialog(QDialog):
    """Dialog to preview and approve/reject planned actions."""

    def __init__(self, plan: dict, parent=None):
        """Initialize the dialog.
        
        Args:
            plan: The action plan dict to preview.
            parent: Parent widget.
        """
        super().__init__(parent)
        self.plan = plan
        self.user_choice = "cancel"
        self._init_ui()

    def _init_ui(self):
        """Initialize the UI components."""
        self.setWindowTitle("Plan Preview")
        self.setMinimumSize(500, 400)
        
        layout = QVBoxLayout()
        
        title_label = QLabel("Planned Actions")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        layout.addWidget(title_label)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setMinimumHeight(250)
        
        content = QWidget()
        content_layout = QVBoxLayout()
        
        actions = self.plan.get("actions", [])
        
        for i, action in enumerate(actions):
            action_label = QLabel(f"{i+1}. {self._format_action(action)}")
            action_label.setWordWrap(True)
            content_layout.addWidget(action_label)
        
        content.setLayout(content_layout)
        scroll.setWidget(content)
        layout.addWidget(scroll)
        
        layout.addWidget(QLabel("Edit Plan (JSON):"))
        
        self.json_editor = QTextEdit()
        import json
        self.json_editor.setPlainText(json.dumps(self.plan, indent=2))
        self.json_editor.setMinimumHeight(100)
        layout.addWidget(self.json_editor)
        
        button_layout = QHBoxLayout()
        
        self.run_btn = QPushButton("Run")
        self.run_btn.clicked.connect(self._on_run)
        button_layout.addWidget(self.run_btn)
        
        self.edit_btn = QPushButton("Edit")
        self.edit_btn.clicked.connect(self._on_edit)
        button_layout.addWidget(self.edit_btn)
        
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.clicked.connect(self._on_cancel)
        button_layout.addWidget(self.cancel_btn)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)

    def _format_action(self, action: dict) -> str:
        """Format an action as a human-readable sentence."""
        action_type = action.get("type", "unknown")
        params = action.get("parameters", {})
        
        if action_type == "open_app":
            return f"Open the application '{params.get('name', 'unknown')}'"
        elif action_type == "open_browser":
            return f"Open {params.get('browser', 'browser')}"
        elif action_type == "navigate":
            return f"Navigate to '{params.get('url', 'unknown')}'"
        elif action_type == "system_volume":
            if "action" in params:
                return f"{params['action'].capitalize()} the system volume"
            elif "level" in params:
                return f"Set volume to {params['level']}%"
        elif action_type == "system_brightness":
            if "level" in params:
                return f"Set brightness to {params['level']}%"
        elif action_type == "system_lock":
            return "Lock the screen"
        elif action_type == "system_sleep":
            return "Put the system to sleep"
        elif action_type == "system_shutdown":
            return f"Shutdown in {params.get('delay', 60)} seconds"
        elif action_type == "system_restart":
            return f"Restart in {params.get('delay', 60)} seconds"
        elif action_type == "speak":
            return f"Speak: '{params.get('text', '')}'"
        elif action_type == "click":
            target = params.get("target", "unknown")
            return f"Click on '{target}'"
        elif action_type == "type_text":
            return f"Type text: '{params.get('text', '')}'"
        elif action_type == "screenshot":
            return "Take a screenshot"
        elif action_type == "close_app":
            return f"Close the application '{params.get('name', 'unknown')}'"
        else:
            return f"Execute: {action_type} ({params})"

    def _on_run(self):
        """Handle Run button click."""
        self.user_choice = "run"
        self.accept()

    def _on_edit(self):
        """Handle Edit button click."""
        self.user_choice = "edit"
        try:
            import json
            edited = json.loads(self.json_editor.toPlainText())
            self.plan = edited
            self.accept()
        except json.JSONDecodeError as e:
            from PyQt6.QtWidgets import QMessageBox
            QMessageBox.warning(self, "Invalid JSON", f"Invalid JSON: {e}")

    def _on_cancel(self):
        """Handle Cancel button click."""
        self.user_choice = "cancel"
        self.reject()
