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

/* ── Tab Widget ───────────────────────────────────────── */
QTabWidget::pane {
    border: 1px solid #333355;
    border-radius: 6px;
    background-color: #0f0f23;
}

QTabBar::tab {
    background-color: #16213e;
    color: #e0e0e0;
    border: 1px solid #333355;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 16px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #0f0f23;
    color: #00d4ff;
}

QTabBar::tab:hover {
    background-color: #1a295c;
}

/* ── Combo Box ────────────────────────────────────────── */
QComboBox {
    background-color: #16213e;
    color: #e0e0e0;
    border: 1px solid #333355;
    border-radius: 4px;
    padding: 4px 8px;
}

QComboBox::drop-down {
    border: none;
}

QComboBox::down-arrow {
    image: none;
    border-left: 5px solid transparent;
    border-right: 5px solid transparent;
    border-top: 5px solid #e0e0e0;
}

/* ── Spin Box ─────────────────────────────────────────── */
QSpinBox, QDoubleSpinBox {
    background-color: #16213e;
    color: #e0e0e0;
    border: 1px solid #333355;
    border-radius: 4px;
    padding: 4px;
}

/* ── Menu ──────────────────────────────────────────────── */
QMenuBar {
    background-color: #16213e;
    color: #e0e0e0;
}

QMenuBar::item:selected {
    background-color: #1a295c;
}

QMenu {
    background-color: #16213e;
    color: #e0e0e0;
    border: 1px solid #333355;
}

QMenu::item:selected {
    background-color: #1a295c;
}

/* ── System Tray ──────────────────────────────────────── */
QSystemTrayIcon {
    background-color: transparent;
}
"""
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

LIGHT_THEME = """
/* ── Global ───────────────────────────────────────────── */
QWidget {
    background-color: #ffffff;
    color: #333333;
    font-family: "Segoe UI", "Consolas", sans-serif;
    font-size: 13px;
}

/* ── Main Window ──────────────────────────────────────── */
QMainWindow {
    background-color: #f5f5f5;
}

/* ── Labels ───────────────────────────────────────────── */
QLabel {
    color: #333333;
    padding: 2px;
}

QLabel#title_label {
    font-size: 20px;
    font-weight: bold;
    color: #0066cc;
    padding: 8px;
}

QLabel#status_label {
    font-size: 14px;
    font-weight: bold;
    padding: 6px 12px;
    border-radius: 6px;
    background-color: #e0e0e0;
}

QLabel#status_label[status="listening"] {
    color: #00aa55;
    background-color: #e0f5e9;
    border: 1px solid #00aa55;
}

QLabel#status_label[status="processing"] {
    color: #cc8800;
    background-color: #fff5e0;
    border: 1px solid #cc8800;
}

QLabel#status_label[status="executing"] {
    color: #0066cc;
    background-color: #e0f0ff;
    border: 1px solid #0066cc;
}

QLabel#status_label[status="idle"] {
    color: #888888;
    background-color: #f5f5f5;
    border: 1px solid #cccccc;
}

QLabel#status_label[status="error"] {
    color: #cc0000;
    background-color: #ffe0e0;
    border: 1px solid #cc0000;
}

/* ── Buttons ──────────────────────────────────────────── */
QPushButton {
    background-color: #e0e0e0;
    color: #333333;
    border: 1px solid #cccccc;
    border-radius: 6px;
    padding: 8px 16px;
    font-size: 13px;
    font-weight: bold;
    min-height: 24px;
}

QPushButton:hover {
    background-color: #d0d0d0;
    border-color: #0066cc;
}

QPushButton:pressed {
    background-color: #c0c0c0;
}

QPushButton#start_btn {
    background-color: #006644;
    border-color: #00aa55;
    color: #ffffff;
    font-size: 14px;
}

QPushButton#start_btn:hover {
    background-color: #008855;
}

QPushButton#stop_btn {
    background-color: #cc0000;
    border-color: #ff4444;
    color: #ffffff;
    font-size: 14px;
}

QPushButton#stop_btn:hover {
    background-color: #ee0000;
}

/* ── Text Areas ───────────────────────────────────────── */
QTextEdit, QPlainTextEdit {
    background-color: #ffffff;
    color: #333333;
    border: 1px solid #cccccc;
    border-radius: 6px;
    padding: 8px;
    font-family: "Cascadia Code", "Consolas", monospace;
    font-size: 12px;
    selection-background-color: #c0e0ff;
}

/* ── Group Boxes ──────────────────────────────────────── */
QGroupBox {
    border: 1px solid #cccccc;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: bold;
    color: #0066cc;
}

QGroupBox::title {
    subcontrol-origin: margin;
    left: 12px;
    padding: 0 6px;
}

/* ── Scroll Bars ──────────────────────────────────────── */
QScrollBar:vertical {
    background-color: #f5f5f5;
    width: 10px;
    border-radius: 5px;
}

QScrollBar::handle:vertical {
    background-color: #cccccc;
    border-radius: 5px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #aaaaaa;
}

QScrollBar:horizontal {
    background-color: #f5f5f5;
    height: 10px;
    border-radius: 5px;
}

QScrollBar::handle:horizontal {
    background-color: #cccccc;
    border-radius: 5px;
}

/* ── Check Boxes ──────────────────────────────────────── */
QCheckBox {
    spacing: 8px;
    color: #333333;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #cccccc;
    border-radius: 4px;
    background-color: #ffffff;
}

QCheckBox::indicator:checked {
    background-color: #0066cc;
    border-color: #0066cc;
}

/* ── Splitter ─────────────────────────────────────────── */
QSplitter::handle {
    background-color: #cccccc;
    width: 2px;
}

QSplitter::handle:hover {
    background-color: #0066cc;
}

/* ── Tool Tips ────────────────────────────────────────── */
QToolTip {
    background-color: #ffffff;
    color: #333333;
    border: 1px solid #0066cc;
    border-radius: 4px;
    padding: 4px;
}

/* ── Dialog ───────────────────────────────────────────── */
QDialog {
    background-color: #f5f5f5;
}

QMessageBox {
    background-color: #f5f5f5;
}
"""
