"""Windows auto-startup installer.

Adds Max to Windows startup by creating a shortcut in the shell:startup folder,
or by adding a registry entry.
"""

import logging
import os
import sys
from pathlib import Path

logger = logging.getLogger(__name__)

STARTUP_FOLDER = Path(os.environ.get("APPDATA", "")) / r"Microsoft\Windows\Start Menu\Programs\Startup"
SHORTCUT_NAME = "Max AI Agent.lnk"


def get_executable_path() -> str:
    """Get the path of the current executable or script."""
    if getattr(sys, "frozen", False):
        # Running as PyInstaller bundle
        return sys.executable
    else:
        # Running as script
        return sys.executable  # python.exe


def get_script_path() -> str:
    """Get the path of the main.py script."""
    return str(Path(__file__).parent.parent / "main.py")


def install_startup() -> bool:
    """Add Max to Windows startup via shortcut."""
    try:
        import win32com.client

        shortcut_path = STARTUP_FOLDER / SHORTCUT_NAME
        
        shell = win32com.client.Dispatch("WScript.Shell")
        shortcut = shell.CreateShortCut(str(shortcut_path))

        if getattr(sys, "frozen", False):
            # PyInstaller executable
            shortcut.TargetPath = sys.executable
        else:
            # Python script
            shortcut.TargetPath = sys.executable
            shortcut.Arguments = f'"{get_script_path()}"'

        shortcut.WorkingDirectory = str(Path(__file__).parent.parent)
        shortcut.Description = "Max AI Desktop Agent"
        shortcut.save()

        logger.info(f"Startup shortcut created: {shortcut_path}")
        return True

    except ImportError:
        # Fallback: use registry
        return _install_startup_registry()
    except Exception as e:
        logger.error(f"Failed to create startup shortcut: {e}")
        return False


def _install_startup_registry() -> bool:
    """Add Max to Windows startup via registry."""
    try:
        import winreg

        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        
        if getattr(sys, "frozen", False):
            command = f'"{sys.executable}"'
        else:
            command = f'"{sys.executable}" "{get_script_path()}"'

        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            key_path,
            0,
            winreg.KEY_SET_VALUE,
        )
        winreg.SetValueEx(key, "MaxAIAgent", 0, winreg.REG_SZ, command)
        winreg.CloseKey(key)

        logger.info("Startup registry entry created")
        return True

    except Exception as e:
        logger.error(f"Failed to create startup registry entry: {e}")
        return False


def remove_startup() -> bool:
    """Remove Max from Windows startup."""
    removed = False

    # Remove shortcut
    shortcut_path = STARTUP_FOLDER / SHORTCUT_NAME
    if shortcut_path.exists():
        try:
            shortcut_path.unlink()
            logger.info("Startup shortcut removed")
            removed = True
        except Exception as e:
            logger.error(f"Failed to remove startup shortcut: {e}")

    # Remove registry entry
    try:
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key = winreg.OpenKey(
            winreg.HKEY_CURRENT_USER,
            key_path,
            0,
            winreg.KEY_SET_VALUE,
        )
        try:
            winreg.DeleteValue(key, "MaxAIAgent")
            logger.info("Startup registry entry removed")
            removed = True
        except FileNotFoundError:
            pass  # Entry doesn't exist
        winreg.CloseKey(key)
    except Exception as e:
        logger.error(f"Failed to remove startup registry entry: {e}")

    return removed


def is_startup_enabled() -> bool:
    """Check if Max is configured to start on boot."""
    # Check shortcut
    shortcut_path = STARTUP_FOLDER / SHORTCUT_NAME
    if shortcut_path.exists():
        return True

    # Check registry
    try:
        import winreg
        key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
        try:
            winreg.QueryValueEx(key, "MaxAIAgent")
            winreg.CloseKey(key)
            return True
        except FileNotFoundError:
            winreg.CloseKey(key)
    except Exception:
        pass

    return False
