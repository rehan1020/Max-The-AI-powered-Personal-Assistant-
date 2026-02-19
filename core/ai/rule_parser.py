"""Rule-based command parser — handle simple commands without LLM.

This module intercepts common commands and converts them to action plans
without invoking the LLM. This improves speed, safety, and predictability.

Falls back to LLM only when a command cannot be matched to a rule.
"""

import json
import logging
import re
from typing import Optional

logger = logging.getLogger(__name__)

# Simple command patterns and their corresponding action plans
SIMPLE_COMMAND_RULES = {
    # Open apps/browsers
    r"^(?:open|launch|start)\s+(?:google\s+)?chrome(?:\s+browser)?$": {
        "task_type": "single_step",
        "actions": [{"type": "open_browser", "parameters": {"browser": "chrome"}}],
    },
    r"^(?:open|launch|start)\s+(?:mozilla\s+)?firefox(?:\s+browser)?$": {
        "task_type": "single_step",
        "actions": [{"type": "open_app", "parameters": {"name": "firefox"}}],
    },
    r"^(?:open|launch|start)\s+(?:microsoft\s+)?edge(?:\s+browser)?$": {
        "task_type": "single_step",
        "actions": [{"type": "open_app", "parameters": {"name": "edge"}}],
    },
    
    # Open common apps
    r"^(?:open|launch|start)\s+(?:ms\s+)?word(?:\s+document)?$": {
        "task_type": "single_step",
        "actions": [{"type": "open_app", "parameters": {"name": "winword"}}],
    },
    r"^(?:open|launch|start)\s+(?:ms\s+)?excel(?:\s+sheet)?$": {
        "task_type": "single_step",
        "actions": [{"type": "open_app", "parameters": {"name": "excel"}}],
    },
    r"^(?:open|launch|start)\s+notepad$": {
        "task_type": "single_step",
        "actions": [{"type": "open_app", "parameters": {"name": "notepad"}}],
    },
    r"^(?:open|launch|start)\s+(?:file\s+)?explorer$": {
        "task_type": "single_step",
        "actions": [{"type": "open_app", "parameters": {"name": "explorer"}}],
    },
    r"^(?:open|launch|start)\s+(?:task\s+)?manager$": {
        "task_type": "single_step",
        "actions": [{"type": "open_app", "parameters": {"name": "taskmgr"}}],
    },
    r"^(?:open|launch|start)\s+calculator$": {
        "task_type": "single_step",
        "actions": [{"type": "open_app", "parameters": {"name": "calculator"}}],
    },
    r"^(?:open|launch|start)\s+settings$": {
        "task_type": "single_step",
        "actions": [{"type": "open_app", "parameters": {"name": "settings"}}],
    },
    
    # Volume control
    r"^(?:mute|silence)(?:\s+(?:the\s+)?(?:audio|sound|volume))?$": {
        "task_type": "single_step",
        "actions": [{"type": "system_volume", "parameters": {"action": "mute"}}],
    },
    r"^unmute(?:\s+(?:the\s+)?(?:audio|sound|volume))?$": {
        "task_type": "single_step",
        "actions": [{"type": "system_volume", "parameters": {"action": "unmute"}}],
    },
    r"^set\s+(?:the\s+)?volume\s+to\s+(\d+)(?:\s*%)?$": "volume_level",  # Special handler
    r"^volume\s+(\d+)(?:\s*%)?$": "volume_level",
    
    # Brightness control
    r"^set\s+(?:the\s+)?brightness\s+to\s+(\d+)(?:\s*%)?$": "brightness_level",
    r"^brightness\s+(\d+)(?:\s*%)?$": "brightness_level",
    
    # System power
    r"^(?:lock|lock\s+(?:the\s+)?screen|lock\s+up)$": {
        "task_type": "single_step",
        "actions": [{"type": "system_lock", "parameters": {}}],
    },
    r"^(?:sleep|put\s+(?:the\s+)?(?:system|computer)\s+to\s+sleep|go\s+to\s+sleep)$": {
        "task_type": "single_step",
        "actions": [{"type": "system_sleep", "parameters": {"delay": 0}}],
    },
    r"^(?:shutdown|shut\s+down|power\s+off)(?:\s+in\s+(\d+)\s+(?:second|sec))?$": "shutdown",
    r"^(?:restart|reboot)(?:\s+in\s+(\d+)\s+(?:second|sec))?$": "restart",
    
    # WiFi/Bluetooth
    r"^(?:turn\s+)?wifi\s+(?:on|off)$": "wifi",
    r"^(?:toggle|switch)\s+wifi$": {
        "task_type": "single_step",
        "actions": [{"type": "system_wifi", "parameters": {"action": "toggle"}}],
    },
    r"^(?:turn\s+)?bluetooth\s+(?:on|off)$": "bluetooth",
    r"^(?:toggle|switch)\s+bluetooth$": {
        "task_type": "single_step",
        "actions": [{"type": "system_bluetooth", "parameters": {"action": "toggle"}}],
    },
}


def parse_simple_command(text: str) -> Optional[dict]:
    """Try to parse command as a simple rule-based action.
    
    Args:
        text: User command text (should be normalized/lowercase)
        
    Returns:
        Action plan dict if matched, None to fall back to LLM
    """
    text_lower = text.lower().strip()
    
    # Try each pattern
    for pattern, handler in SIMPLE_COMMAND_RULES.items():
        match = re.match(pattern, text_lower)
        if match:
            logger.info(f"Rule matched: {pattern}")
            
            # Handler is a dict — return as-is
            if isinstance(handler, dict):
                return handler
            
            # Handler is a function reference string — call appropriate handler
            if handler == "volume_level":
                level = int(match.group(1))
                return {
                    "task_type": "single_step",
                    "actions": [{"type": "system_volume", "parameters": {"level": level}}],
                }
            elif handler == "brightness_level":
                level = int(match.group(1))
                return {
                    "task_type": "single_step",
                    "actions": [{"type": "system_brightness", "parameters": {"level": level}}],
                }
            elif handler == "shutdown":
                delay = 60
                if match.group(1):
                    delay = int(match.group(1))
                return {
                    "task_type": "single_step",
                    "actions": [{"type": "system_shutdown", "parameters": {"delay": delay}}],
                }
            elif handler == "restart":
                delay = 60
                if match.group(1):
                    delay = int(match.group(1))
                return {
                    "task_type": "single_step",
                    "actions": [{"type": "system_restart", "parameters": {"delay": delay}}],
                }
            elif handler == "wifi":
                action = "on" if "on" in text_lower else "off"
                return {
                    "task_type": "single_step",
                    "actions": [{"type": "system_wifi", "parameters": {"action": action}}],
                }
            elif handler == "bluetooth":
                action = "on" if "on" in text_lower else "off"
                return {
                    "task_type": "single_step",
                    "actions": [{"type": "system_bluetooth", "parameters": {"action": action}}],
                }
    
    # No match found
    return None


def should_use_llm(complexity_only: bool = False) -> bool:
    """Determine if LLM should be used.
    
    Args:
        complexity_only: If True, command is complex enough to require LLM
        
    Returns:
        True if LLM should be used, False to reject complex commands
    """
    import config
    
    if config.LLM_PROVIDER == "none":
        return False
    
    if complexity_only and config.SIMPLE_COMMANDS_ONLY:
        logger.warning("Complex command rejected: SIMPLE_COMMANDS_ONLY=True")
        return False
    
    return True
