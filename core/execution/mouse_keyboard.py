"""Mouse and keyboard control using PyAutoGUI.

Used as fallback when DOM-based browser automation isn't possible,
and for desktop-level interactions.
"""

import logging
import time
from typing import Optional

import pyautogui

logger = logging.getLogger(__name__)

# Safety settings
pyautogui.FAILSAFE = True       # Move mouse to corner to abort
pyautogui.PAUSE = 0.1           # Small pause between actions


def move_mouse(**params) -> dict:
    """Move mouse to absolute coordinates."""
    x = params.get("x", 0)
    y = params.get("y", 0)
    duration = params.get("duration", 0.3)

    try:
        pyautogui.moveTo(x, y, duration=duration)
        logger.info(f"Mouse moved to ({x}, {y})")
        return {"success": True, "message": f"Mouse moved to ({x}, {y})"}
    except Exception as e:
        logger.error(f"Mouse move failed: {e}")
        return {"success": False, "message": f"Mouse move failed: {e}"}


def click(**params) -> dict:
    """Click at coordinates or current position."""
    x = params.get("x")
    y = params.get("y")
    button = params.get("button", "left")
    clicks = params.get("clicks", 1)

    try:
        if x is not None and y is not None:
            pyautogui.click(x=int(x), y=int(y), button=button, clicks=clicks)
            logger.info(f"Clicked at ({x}, {y}) [{button}]")
        else:
            pyautogui.click(button=button, clicks=clicks)
            logger.info(f"Clicked at current position [{button}]")
        return {"success": True, "message": "Clicked"}
    except Exception as e:
        logger.error(f"Click failed: {e}")
        return {"success": False, "message": f"Click failed: {e}"}


def type_text(**params) -> dict:
    """Type text using keyboard."""
    text = params.get("text", "")
    interval = params.get("interval", 0.02)

    try:
        pyautogui.typewrite(text, interval=interval) if text.isascii() else pyautogui.write(text)
        logger.info(f"Typed: {text[:50]}")
        return {"success": True, "message": f"Typed: {text[:50]}"}
    except Exception as e:
        # Fallback to pyperclip for non-ASCII
        try:
            import pyperclip
            pyperclip.copy(text)
            pyautogui.hotkey("ctrl", "v")
            logger.info(f"Typed (clipboard): {text[:50]}")
            return {"success": True, "message": f"Typed: {text[:50]}"}
        except Exception as e2:
            logger.error(f"Type failed: {e2}")
            return {"success": False, "message": f"Type failed: {e2}"}


def press_key(**params) -> dict:
    """Press a key or key combination."""
    key = params.get("key", "")

    try:
        if "+" in key:
            # Key combination: ctrl+c, alt+f4, etc.
            keys = [k.strip() for k in key.split("+")]
            pyautogui.hotkey(*keys)
        else:
            pyautogui.press(key)

        logger.info(f"Pressed key: {key}")
        return {"success": True, "message": f"Pressed: {key}"}
    except Exception as e:
        logger.error(f"Key press failed: {e}")
        return {"success": False, "message": f"Key press failed: {e}"}


def get_mouse_position() -> tuple:
    """Get current mouse position."""
    pos = pyautogui.position()
    return (pos.x, pos.y)


def get_screen_size() -> tuple:
    """Get screen resolution."""
    size = pyautogui.size()
    return (size.width, size.height)
