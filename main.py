"""Max — AI Voice-Controlled Windows Desktop Agent.

Entry point. Launches the GUI and orchestrator.
"""

import logging
import sys
import os
from pathlib import Path

# Ensure project root is on path
PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

# ── Fix DLL conflicts: register torch DLL directory BEFORE PyQt6 loads ──
# On Windows, PyQt6 and PyTorch both bundle native DLLs.
# If PyQt6 loads first it can break torch's c10.dll initialization.
try:
    import torch
    torch_lib = Path(torch.__file__).parent / "lib"
    if torch_lib.exists() and hasattr(os, "add_dll_directory"):
        os.add_dll_directory(str(torch_lib))
except Exception:
    pass  # torch not installed or other issue — will be handled later

import config


def setup_logging():
    """Configure logging to both file and console."""
    log_format = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"

    handlers = [
        logging.StreamHandler(sys.stdout),
        logging.FileHandler(str(config.LOG_FILE), encoding="utf-8"),
    ]

    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL, logging.INFO),
        format=log_format,
        datefmt=date_format,
        handlers=handlers,
    )

    # Suppress noisy loggers
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    logging.getLogger("PIL").setLevel(logging.WARNING)
    logging.getLogger("easyocr").setLevel(logging.WARNING)


def check_internet() -> bool:
    """Quick internet connectivity check."""
    try:
        import httpx
        resp = httpx.head("https://openrouter.ai", timeout=5)
        return resp.status_code < 500
    except Exception:
        return False


def main():
    """Launch Max Desktop Agent."""
    setup_logging()
    logger = logging.getLogger(__name__)
    logger.info("=" * 60)
    logger.info("  MAX — AI Voice-Controlled Desktop Agent")
    logger.info("=" * 60)

    # Validate provider config
    if config.LLM_PROVIDER in ("cloud", "auto") and not config.OPENROUTER_API_KEY:
        logger.warning("OPENROUTER_API_KEY not set — cloud LLM will not work.")
    logger.info(f"LLM mode: {config.LLM_PROVIDER}")

    # Launch PyQt6 application
    from PyQt6.QtWidgets import QApplication
    from gui.main_window import MaxMainWindow
    from core.orchestrator import Orchestrator

    app = QApplication(sys.argv)
    app.setApplicationName("Max AI Agent")
    app.setApplicationDisplayName("Max — AI Desktop Agent")

    # Create main window
    window = MaxMainWindow()

    # Create orchestrator with GUI reference
    orchestrator = Orchestrator(gui=window)

    # Wire up GUI callbacks
    window.on_start = orchestrator.start
    window.on_stop = orchestrator.stop
    window.on_safe_mode_changed = lambda enabled: setattr(
        orchestrator.safety, "safe_mode", enabled
    )

    # Check internet (only relevant for cloud modes)
    if config.LLM_PROVIDER == "local":
        window.status_bar.set_internet_status(True)  # doesn't matter for local
        window.add_system_message(f"LLM: local ({config.OLLAMA_MODEL})")
    else:
        online = check_internet()
        window.status_bar.set_internet_status(online)
        if not online:
            if config.LLM_PROVIDER == "cloud":
                window.add_system_message("⚠ No internet. Cloud LLM will not work.")
            else:
                window.add_system_message("⚠ No internet. Will rely on local LLM.")

    # Show window
    window.show()
    window.add_system_message("Max initialized. Click 'Start Listening' to begin.")

    # Run event loop
    exit_code = app.exec()

    # Cleanup
    orchestrator.cleanup()
    logger.info("Max shut down cleanly.")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
