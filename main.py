"""Max — AI Voice-Controlled Desktop Agent.

Entry point. Launches the GUI and orchestrator.
"""

import logging
import sys
import os
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.resolve()
sys.path.insert(0, str(PROJECT_ROOT))

try:
    import torch
    torch_lib = Path(torch.__file__).parent / "lib"
    if torch_lib.exists() and hasattr(os, "add_dll_directory"):
        os.add_dll_directory(str(torch_lib))
except Exception:
    pass

import config


from core.logger import logger

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
    logger.info("=" * 60)
    logger.info("  MAX — AI Voice-Controlled Desktop Agent")
    logger.info("=" * 60)

    if config.LLM_PROVIDER in ("cloud", "auto") and not config.OPENROUTER_API_KEY:
        logger.warning("OPENROUTER_API_KEY not set — cloud LLM will not work.")
    logger.info(f"LLM mode: {config.LLM_PROVIDER}")

    from PyQt6.QtWidgets import QApplication
    from gui.main_window import MaxMainWindow
    from core.orchestrator import Orchestrator

    app = QApplication(sys.argv)
    app.setApplicationName("Max AI Agent")
    app.setApplicationDisplayName("Max — AI Desktop Agent")

    from core.startup_check import run_all_checks, has_critical_failures
    logger.info("Running startup checks...")
    check_results = run_all_checks()
    
    critical_failed = has_critical_failures(check_results)
    if critical_failed:
        from gui.startup_dialog import StartupDialog
        startup_dialog = StartupDialog(check_results)
        startup_dialog.exec()
        logger.warning("Some critical startup checks failed, but continuing...")

    logger.info("Pre-loading Whisper models...")
    try:
        from faster_whisper import WhisperModel
        device = config.WHISPER_DEVICE
        compute_type = "float16" if device == "cuda" else "int8"
        
        WhisperModel("tiny", device=device, compute_type=compute_type)
        logger.info("Whisper 'tiny' model ready")
        
        WhisperModel("small", device=device, compute_type=compute_type)
        logger.info("Whisper 'small' model ready")
    except Exception as e:
        logger.warning(f"Failed to pre-load models: {e}")

    window = MaxMainWindow()

    orchestrator = Orchestrator(gui=window)

    window.on_start = orchestrator.start
    window.on_stop = orchestrator.stop
    window.on_safe_mode_changed = lambda enabled: setattr(
        orchestrator.safety, "safe_mode", enabled
    )

    if config.LLM_PROVIDER == "local":
        window.status_bar.set_internet_status(True)
        window.add_system_message(f"LLM: local ({config.OLLAMA_MODEL})")
    else:
        online = check_internet()
        window.status_bar.set_internet_status(online)
        if not online:
            if config.LLM_PROVIDER == "cloud":
                window.add_system_message("No internet. Cloud LLM will not work.")
            else:
                window.add_system_message("No internet. Will rely on local LLM.")

    window.show()
    window.add_system_message("Max initialized. Click 'Start Listening' to begin.")

    exit_code = app.exec()

    orchestrator.cleanup()
    logger.info("Max shut down cleanly.")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
