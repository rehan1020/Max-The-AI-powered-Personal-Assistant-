"""QSS Stylesheet for Max Desktop Agent GUI.

Professional dark theme with accent colors.
"""

DARK_THEME = """
/* ── Global ───────────────────────────────────────────── */
QWidget {
    background-color: #1a1a2e;
    color: #e0e0e0;
    font-family: "Segoe UI", "Consolas", sans-serif;
    font-size: 13px;
}

/* ── Main Window ──────────────────────────────────────── */
QMainWindow {
    background-color: #1a1a2e;
}

/* ── Labels ───────────────────────────────────────────── */
QLabel {
    color: #e0e0e0;
    padding: 2px;
}

QLabel#title_label {
    font-size: 20px;
    font-weight: bold;
    color: #00d4ff;
    padding: 8px;
}

QLabel#status_label {
    font-size: 14px;
    font-weight: bold;
    padding: 6px 12px;
    border-radius: 6px;
    background-color: #16213e;
}

QLabel#status_label[status="listening"] {
    color: #00ff88;
    background-color: #0d3320;
    border: 1px solid #00ff88;
}

QLabel#status_label[status="processing"] {
    color: #ffaa00;
    background-color: #332d00;
    border: 1px solid #ffaa00;
}

QLabel#status_label[status="executing"] {
    color: #00d4ff;
    background-color: #002233;
    border: 1px solid #00d4ff;
}

QLabel#status_label[status="idle"] {
    color: #888888;
    background-color: #1a1a2e;
    border: 1px solid #333355;
}

QLabel#status_label[status="error"] {
    color: #ff4444;
    background-color: #331111;
    border: 1px solid #ff4444;
}

/* ── Buttons ──────────────────────────────────────────── */
QPushButton {
    background-color: #16213e;
    color: #e0e0e0;
    border: 1px solid #333355;
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: bold;
    min-height: 24px;
}

QPushButton:hover {
    background-color: #1a295c;
    border-color: #00d4ff;
}

QPushButton:pressed {
    background-color: #0d1b3e;
}

QPushButton#start_btn {
    background-color: #004d40;
    border-color: #00ff88;
    color: #00ff88;
    font-size: 14px;
}

QPushButton#start_btn:hover {
    background-color: #00695c;
}

QPushButton#stop_btn {
    background-color: #4a0000;
    border-color: #ff4444;
    color: #ff4444;
    font-size: 14px;
}

QPushButton#stop_btn:hover {
    background-color: #660000;
}

/* ── Text Areas ───────────────────────────────────────── */
QTextEdit, QPlainTextEdit {
    background-color: #0f0f23;
    color: #c8c8d8;
    border: 1px solid #333355;
    border-radius: 6px;
    padding: 8px;
    font-family: "Cascadia Code", "Consolas", monospace;
    font-size: 12px;
    selection-background-color: #1a295c;
}

/* ── Group Boxes ──────────────────────────────────────── */
QGroupBox {
    border: 1px solid #333355;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: bold;
    color: #00d4ff;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}

/* ── Scroll Bars ──────────────────────────────────────── */
QScrollBar:vertical {
    background-color: #0f0f23;
    width: 10px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background-color: #333355;
    border-radius: 5px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #4444aa;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0;
}

QScrollBar:horizontal {
    background-color: #0f0f23;
    height: 10px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal {
    background-color: #333355;
    border-radius: 5px;
}

/* ── Check Boxes ──────────────────────────────────────── */
QCheckBox {
    spacing: 8px;
    color: #e0e0e0;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #333355;
    border-radius: 4px;
    background-color: #0f0f23;
}

QCheckBox::indicator:checked {
    background-color: #00d4ff;
    border-color: #00d4ff;
}

/* ── Splitter ─────────────────────────────────────────── */
QSplitter::handle {
    background-color: #333355;
    width: 2px;
}

QSplitter::handle:hover {
    background-color: #00d4ff;
}

/* ── Tool Tips ────────────────────────────────────────── */
QToolTip {
    background-color: #16213e;
    color: #e0e0e0;
    border: 1px solid #00d4ff;
    border-radius: 4px;
    padding: 4px;
}

/* ── Dialog ───────────────────────────────────────────── */
QDialog {
    background-color: #1a1a2e;
}

QMessageBox {
    background-color: #1a1a2e;
}
"""
