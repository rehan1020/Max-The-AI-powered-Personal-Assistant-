"""System control — volume, brightness, app launching, software installation.

This module provides a cross-platform interface for system control operations.
All OS-specific code has been moved to core/platform/ adapters.
"""

import time
from pathlib import Path

import pyautogui

from core.logger import logger
from core.platform import get_adapter


def open_app(**params) -> dict:
    """Open an application by name.
    
    Uses the platform adapter and app registry for cross-platform support.
    """
    name = params.get("name", "").strip()
    if not name:
        return {"success": False, "message": "No app name provided"}

    adapter = get_adapter()
    try:
        if adapter.launch_app(name):
            logger.info(f"Opened app: {name}")
            return {"success": True, "message": f"Opened: {name}"}
        else:
            return {"success": False, "message": f"Could not find or open: {name}"}
    except Exception as e:
        logger.error(f"Failed to open '{name}': {e}")
        return {"success": False, "message": f"Failed to open: {name} — {e}"}


def close_app(**params) -> dict:
    """Close an application by name."""
    name = params.get("name", "").strip()
    if not name:
        return {"success": False, "message": "No app name provided"}

    adapter = get_adapter()
    try:
        if adapter.close_app(name):
            logger.info(f"Closed app: {name}")
            return {"success": True, "message": f"Closed: {name}"}
        else:
            return {"success": False, "message": f"Could not close: {name}"}
    except Exception as e:
        logger.error(f"Failed to close app '{name}': {e}")
        return {"success": False, "message": f"Failed to close: {name} — {e}"}


def system_volume(**params) -> dict:
    """Control system volume. Params: level (0-100) or action (mute/unmute/up/down)."""
    adapter = get_adapter()
    
    action = params.get("action", "")
    level = params.get("level")

    try:
        if action == "mute":
            if adapter.mute():
                logger.info("Volume muted")
                return {"success": True, "message": "Muted"}
            return {"success": False, "message": "Mute failed"}
        elif action == "unmute":
            if adapter.unmute():
                logger.info("Volume unmuted")
                return {"success": True, "message": "Unmuted"}
            return {"success": False, "message": "Unmute failed"}
        elif action == "up":
            current = adapter.get_volume()
            new_level = min(100, current + 10)
            if adapter.set_volume(new_level):
                return {"success": True, "message": f"Volume: {new_level}%"}
            return {"success": False, "message": "Volume control failed"}
        elif action == "down":
            current = adapter.get_volume()
            new_level = max(0, current - 10)
            if adapter.set_volume(new_level):
                return {"success": True, "message": f"Volume: {new_level}%"}
            return {"success": False, "message": "Volume control failed"}
        elif level is not None:
            level = max(0, min(100, int(level)))
            if adapter.set_volume(level):
                logger.info(f"Volume set to {level}%")
                return {"success": True, "message": f"Volume: {level}%"}
            return {"success": False, "message": "Volume control failed"}
        else:
            current = adapter.get_volume()
            return {"success": True, "message": f"Current volume: {current}%"}
    except Exception as e:
        logger.error(f"Volume control failed: {e}")
        return {"success": False, "message": f"Volume control failed: {e}"}


def system_brightness(**params) -> dict:
    """Control screen brightness. Params: level (0-100) or action (up/down)."""
    adapter = get_adapter()
    
    action = params.get("action", "")
    level = params.get("level")

    try:
        if action == "up":
            current = adapter.get_brightness()
            new_level = min(100, current + 10)
            if adapter.set_brightness(new_level):
                return {"success": True, "message": f"Brightness: {new_level}%"}
            return {"success": False, "message": "Brightness control failed"}
        elif action == "down":
            current = adapter.get_brightness()
            new_level = max(0, current - 10)
            if adapter.set_brightness(new_level):
                return {"success": True, "message": f"Brightness: {new_level}%"}
            return {"success": False, "message": "Brightness control failed"}
        elif level is not None:
            level = max(0, min(100, int(level)))
            if adapter.set_brightness(level):
                logger.info(f"Brightness set to {level}%")
                return {"success": True, "message": f"Brightness: {level}%"}
            return {"success": False, "message": "Brightness control failed"}
        else:
            current = adapter.get_brightness()
            return {"success": True, "message": f"Current brightness: {current}%"}
    except Exception as e:
        logger.error(f"Brightness control failed: {e}")
        return {"success": False, "message": f"Brightness control failed: {e}"}


def install_software(**params) -> dict:
    """Install software via the OS package manager."""
    name = params.get("name", "").strip()
    if not name:
        return {"success": False, "message": "No software name provided"}

    adapter = get_adapter()
    try:
        if adapter.install_software(name):
            logger.info(f"Installed: {name}")
            return {"success": True, "message": f"Installed: {name}"}
        return {"success": False, "message": f"Install failed: {name}"}
    except Exception as e:
        logger.error(f"Install failed: {e}")
        return {"success": False, "message": f"Install failed: {e}"}


def system_sleep(**params) -> dict:
    """Put the system to sleep. Params: delay (seconds, optional)."""
    delay = int(params.get("delay", 0))
    
    adapter = get_adapter()
    try:
        if delay > 0:
            logger.info(f"System sleep in {delay} seconds")
            time.sleep(delay)
        if adapter.sleep():
            logger.info("System is sleeping")
            return {"success": True, "message": "System is sleeping"}
        return {"success": False, "message": "Sleep failed"}
    except Exception as e:
        logger.error(f"Sleep failed: {e}")
        return {"success": False, "message": f"Sleep failed: {e}"}


def system_lock(**params) -> dict:
    """Lock the screen."""
    adapter = get_adapter()
    try:
        if adapter.lock_screen():
            logger.info("Screen locked")
            return {"success": True, "message": "Screen locked"}
        return {"success": False, "message": "Lock failed"}
    except Exception as e:
        logger.error(f"Lock failed: {e}")
        return {"success": False, "message": f"Lock failed: {e}"}


def system_shutdown(**params) -> dict:
    """Shut down the system. Params: delay (seconds)."""
    delay = int(params.get("delay", 60))
    
    adapter = get_adapter()
    try:
        if adapter.shutdown(delay):
            logger.info(f"Shutdown scheduled in {delay} seconds")
            return {"success": True, "message": f"Shutdown in {delay}s"}
        return {"success": False, "message": "Shutdown failed"}
    except Exception as e:
        logger.error(f"Shutdown failed: {e}")
        return {"success": False, "message": f"Shutdown failed: {e}"}


def system_restart(**params) -> dict:
    """Restart the system. Params: delay (seconds)."""
    delay = int(params.get("delay", 60))
    
    adapter = get_adapter()
    try:
        if adapter.restart(delay):
            logger.info(f"Restart scheduled in {delay} seconds")
            return {"success": True, "message": f"Restart in {delay}s"}
        return {"success": False, "message": "Restart failed"}
    except Exception as e:
        logger.error(f"Restart failed: {e}")
        return {"success": False, "message": f"Restart failed: {e}"}


def system_wifi(**params) -> dict:
    """Toggle WiFi on/off. Params: action (on/off/toggle)."""
    action = params.get("action", "toggle").lower()
    
    adapter = get_adapter()
    try:
        if action == "toggle":
            current = adapter.get_wifi_status()
            if adapter.set_wifi(not current):
                state = "off" if current else "on"
                logger.info(f"WiFi toggled: {state}")
                return {"success": True, "message": f"WiFi {state}"}
        else:
            enabled = (action == "on")
            if adapter.set_wifi(enabled):
                logger.info(f"WiFi {action}")
                return {"success": True, "message": f"WiFi {action}"}
        return {"success": False, "message": f"WiFi control failed: {action}"}
    except Exception as e:
        logger.error(f"WiFi control failed: {e}")
        return {"success": False, "message": f"WiFi control failed: {e}"}


def system_bluetooth(**params) -> dict:
    """Toggle Bluetooth on/off. Params: action (on/off/toggle)."""
    action = params.get("action", "toggle").lower()
    
    adapter = get_adapter()
    try:
        if action == "toggle":
            current = adapter.get_bluetooth_status()
            if adapter.set_bluetooth(not current):
                state = "off" if current else "on"
                logger.info(f"Bluetooth toggled: {state}")
                return {"success": True, "message": f"Bluetooth {state}"}
        else:
            enabled = (action == "on")
            if adapter.set_bluetooth(enabled):
                logger.info(f"Bluetooth {action}")
                return {"success": True, "message": f"Bluetooth {action}"}
        return {"success": False, "message": f"Bluetooth control failed: {action}"}
    except Exception as e:
        logger.error(f"Bluetooth control failed: {e}")
        return {"success": False, "message": f"Bluetooth control failed: {e}"}


def system_screensaver(**params) -> dict:
    """Control screen saver. Params: action (on/off)."""
    action = params.get("action", "on").lower()
    
    try:
        if action == "on":
            logger.info("Screensaver started")
            return {"success": True, "message": "Screensaver started"}
        else:
            pyautogui.moveTo(pyautogui.position()[0] + 1, pyautogui.position()[1] + 1)
            logger.info("Screensaver disabled")
            return {"success": True, "message": "Screensaver disabled"}
    except Exception as e:
        logger.error(f"Screensaver control failed: {e}")
        return {"success": False, "message": f"Screensaver control failed: {e}"}


def system_mute(**params) -> dict:
    """Mute system audio."""
    adapter = get_adapter()
    try:
        if adapter.mute():
            logger.info("System muted")
            return {"success": True, "message": "System muted"}
        return {"success": False, "message": "Mute failed"}
    except Exception as e:
        logger.error(f"Mute failed: {e}")
        return {"success": False, "message": f"Mute failed: {e}"}


def system_unmute(**params) -> dict:
    """Unmute system audio."""
    adapter = get_adapter()
    try:
        if adapter.unmute():
            logger.info("System unmuted")
            return {"success": True, "message": "System unmuted"}
        return {"success": False, "message": "Unmute failed"}
    except Exception as e:
        logger.error(f"Unmute failed: {e}")
        return {"success": False, "message": f"Unmute failed: {e}"}


def get_clipboard(**params) -> dict:
    """Get clipboard content."""
    adapter = get_adapter()
    try:
        text = adapter.get_clipboard()
        return {"success": True, "message": text}
    except Exception as e:
        logger.error(f"Get clipboard failed: {e}")
        return {"success": False, "message": f"Get clipboard failed: {e}"}


def set_clipboard(**params) -> dict:
    """Set clipboard content."""
    text = params.get("text", "")
    adapter = get_adapter()
    try:
        if adapter.set_clipboard(text):
            return {"success": True, "message": "Clipboard set"}
        return {"success": False, "message": "Set clipboard failed"}
    except Exception as e:
        logger.error(f"Set clipboard failed: {e}")
        return {"success": False, "message": f"Set clipboard failed: {e}"}


def send_notification(**params) -> dict:
    """Send a notification."""
    title = params.get("title", "Max AI")
    message = params.get("message", "")
    adapter = get_adapter()
    try:
        if adapter.send_notification(title, message):
            return {"success": True, "message": "Notification sent"}
        return {"success": False, "message": "Notification failed"}
    except Exception as e:
        logger.error(f"Notification failed: {e}")
        return {"success": False, "message": f"Notification failed: {e}"}


def get_battery(**params) -> dict:
    """Get battery percentage."""
    adapter = get_adapter()
    try:
        percent = adapter.get_battery_percent()
        if percent is not None:
            return {"success": True, "message": f"Battery: {percent}%"}
        return {"success": False, "message": "No battery"}
    except Exception as e:
        logger.error(f"Battery check failed: {e}")
        return {"success": False, "message": f"Battery check failed: {e}"}


def install_startup(**params) -> dict:
    """Install startup entry."""
    adapter = get_adapter()
    app_path = Path(__file__).parent.parent / "main.py"
    try:
        if adapter.install_startup(app_path):
            return {"success": True, "message": "Startup installed"}
        return {"success": False, "message": "Startup install failed"}
    except Exception as e:
        logger.error(f"Startup install failed: {e}")
        return {"success": False, "message": f"Startup install failed: {e}"}


def remove_startup(**params) -> dict:
    """Remove startup entry."""
    adapter = get_adapter()
    try:
        if adapter.remove_startup():
            return {"success": True, "message": "Startup removed"}
        return {"success": False, "message": "Startup remove failed"}
    except Exception as e:
        logger.error(f"Startup remove failed: {e}")
        return {"success": False, "message": f"Startup remove failed: {e}"}


def is_startup_enabled(**params) -> dict:
    """Check if startup is enabled."""
    adapter = get_adapter()
    try:
        enabled = adapter.is_startup_enabled()
        return {"success": True, "message": "Enabled" if enabled else "Disabled"}
    except Exception as e:
        logger.error(f"Startup check failed: {e}")
        return {"success": False, "message": f"Startup check failed: {e}"}
