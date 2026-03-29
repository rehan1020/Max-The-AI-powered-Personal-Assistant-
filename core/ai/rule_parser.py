"""Rule-based command parser — handle simple commands without LLM.

This module intercepts common commands and converts them to action plans
without invoking the LLM. This improves speed, safety, and predictability.

Falls back to LLM only when a command cannot be matched to a rule.
"""

import json
import re
from datetime import datetime
from typing import Optional

from core.logger import logger

INTERRUPT_PATTERNS = [
    r"^(stop|cancel|halt|abort|never mind|stop that|quit that|quit)$",
]

# Simple command patterns and their corresponding action plans
SIMPLE_COMMAND_RULES = {
    # Interrupt commands (highest priority)
    r"^stop(?:\s+that)?$": "interrupt",
    r"^cancel(?:\s+that)?$": "interrupt",
    r"^halt$": "interrupt",
    r"^abort$": "interrupt",
    r"^never mind$": "interrupt",
    r"^quit(?:\s+that)?$": "interrupt",

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
        "actions": [{"type": "open_app", "parameters": {"name": "microsoft edge"}}],
    },
    
    # Open common apps
    r"^(?:open|launch|start)\s+(?:visual\s+studio\s+)?code$": {
        "task_type": "single_step",
        "actions": [{"type": "open_app", "parameters": {"name": "vscode"}}],
    },
    r"^(?:open|launch|start)\s+spotify$": {
        "task_type": "single_step",
        "actions": [{"type": "open_app", "parameters": {"name": "spotify"}}],
    },
    r"^(?:open|launch|start)\s+discord$": {
        "task_type": "single_step",
        "actions": [{"type": "open_app", "parameters": {"name": "discord"}}],
    },
    r"^(?:open|launch|start)\s+slack$": {
        "task_type": "single_step",
        "actions": [{"type": "open_app", "parameters": {"name": "slack"}}],
    },
    r"^(?:open|launch|start)\s+teams$": {
        "task_type": "single_step",
        "actions": [{"type": "open_app", "parameters": {"name": "teams"}}],
    },
    r"^(?:open|launch|start)\s+zoom$": {
        "task_type": "single_step",
        "actions": [{"type": "open_app", "parameters": {"name": "zoom"}}],
    },
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
        "actions": [{"type": "open_app", "parameters": {"name": "file_manager"}}],
    },
    r"^(?:open|launch|start)\s+(?:file\s+)?manager$": {
        "task_type": "single_step",
        "actions": [{"type": "open_app", "parameters": {"name": "file_manager"}}],
    },
    r"^(?:open|launch|start)\s+(?:task\s+)?manager$": {
        "task_type": "single_step",
        "actions": [{"type": "open_app", "parameters": {"name": "task manager"}}],
    },
    r"^(?:open|launch|start)\s+calculator$": {
        "task_type": "single_step",
        "actions": [{"type": "open_app", "parameters": {"name": "calculator"}}],
    },
    r"^(?:open|launch|start)\s+terminal$": {
        "task_type": "single_step",
        "actions": [{"type": "open_app", "parameters": {"name": "terminal"}}],
    },
    r"^(?:open|launch|start)\s+vlc$": {
        "task_type": "single_step",
        "actions": [{"type": "open_app", "parameters": {"name": "vlc"}}],
    },
    r"^(?:open|launch|start)\s+settings$": {
        "task_type": "single_step",
        "actions": [{"type": "open_app", "parameters": {"name": "settings"}}],
    },

    # Close apps
    r"^(?:close|quit|exit)\s+(.+)$": "close_app",

    # Volume control
    r"^(?:mute|silence)(?:\s+(?:the\s+)?(?:audio|sound|volume))?$": {
        "task_type": "single_step",
        "actions": [{"type": "system_volume", "parameters": {"action": "mute"}}],
    },
    r"^unmute(?:\s+(?:the\s+)?(?:audio|sound|volume))?$": {
        "task_type": "single_step",
        "actions": [{"type": "system_volume", "parameters": {"action": "unmute"}}],
    },
    r"^(?:turn\s+)?volume\s+up$": {
        "task_type": "single_step",
        "actions": [{"type": "system_volume", "parameters": {"action": "up"}}],
    },
    r"^(?:turn\s+)?volume\s+down$": {
        "task_type": "single_step",
        "actions": [{"type": "system_volume", "parameters": {"action": "down"}}],
    },
    r"^(?:turn\s+)?it\s+up$": {
        "task_type": "single_step",
        "actions": [{"type": "system_volume", "parameters": {"action": "up"}}],
    },
    r"^(?:turn\s+)?it\s+down$": {
        "task_type": "single_step",
        "actions": [{"type": "system_volume", "parameters": {"action": "down"}}],
    },
    r"^(?:louder|turn\s+it\s+up)$": {
        "task_type": "single_step",
        "actions": [{"type": "system_volume", "parameters": {"action": "up"}}],
    },
    r"^(?:quieter|softer|turn\s+it\s+down)$": {
        "task_type": "single_step",
        "actions": [{"type": "system_volume", "parameters": {"action": "down"}}],
    },
    r"^(?:max\s+volume|full\s+volume|maximum\s+volume)$": {
        "task_type": "single_step",
        "actions": [{"type": "system_volume", "parameters": {"level": 100}}],
    },
    r"^set\s+(?:the\s+)?volume\s+to\s+(\d+)(?:\s*%)?$": "volume_level",
    r"^volume\s+(\d+)(?:\s*%)?$": "volume_level",
    r"^(?:set\s+)?(?:the\s+)?sound\s+to\s+(\d+)(?:\s*%)?$": "volume_level",
    
    # Brightness control
    r"^set\s+(?:the\s+)?brightness\s+to\s+(\d+)(?:\s*%)?$": "brightness_level",
    r"^brightness\s+(\d+)(?:\s*%)?$": "brightness_level",
    r"^(?:turn\s+)?brightness\s+up$": {
        "task_type": "single_step",
        "actions": [{"type": "system_brightness", "parameters": {"action": "up"}}],
    },
    r"^(?:turn\s+)?brightness\s+down$": {
        "task_type": "single_step",
        "actions": [{"type": "system_brightness", "parameters": {"action": "down"}}],
    },
    r"^(?:max\s+brightness|maximum\s+brightness)$": {
        "task_type": "single_step",
        "actions": [{"type": "system_brightness", "parameters": {"level": 100}}],
    },
    r"^(?:min\s+brightness|minimum\s+brightness)$": {
        "task_type": "single_step",
        "actions": [{"type": "system_brightness", "parameters": {"level": 0}}],
    },
    r"^silent$": {
        "task_type": "single_step",
        "actions": [{"type": "system_volume", "parameters": {"action": "mute"}}],
    },

    # System power
    r"^(?:lock|lock\s+(?:the\s+)?screen|lock\s+up)$": {
        "task_type": "single_step",
        "actions": [{"type": "system_lock", "parameters": {}}],
    },
    r"^(?:sleep|put\s+(?:the\s+)?(?:system|computer)\s+to\s+sleep|go\s+to\s+sleep)$": {
        "task_type": "single_step",
        "actions": [{"type": "system_sleep", "parameters": {"delay": 0}}],
    },
    r"^(?:hibernate)$": {
        "task_type": "single_step",
        "actions": [{"type": "system_hibernate", "parameters": {}}],
    },
    r"^(?:log\s+off|log\s+out|sign\s+out)$": {
        "task_type": "single_step",
        "actions": [{"type": "system_logoff", "parameters": {}}],
    },
    r"^(?:shutdown|shut\s+down|power\s+off)(?:\s+in\s+(\d+)\s+(?:second|sec|minutes|min))?$": "shutdown",
    r"^(?:restart|reboot)(?:\s+in\s+(\d+)\s+(?:second|sec|minutes|min))?$": "restart",
    
    # WiFi/Bluetooth
    r"^(?:turn\s+)?wifi\s+(on|off)$": "wifi",
    r"^(?:toggle|switch)\s+wifi$": {
        "task_type": "single_step",
        "actions": [{"type": "system_wifi", "parameters": {"action": "toggle"}}],
    },
    r"^(?:turn\s+)?bluetooth\s+(on|off)$": "bluetooth",
    r"^(?:toggle|switch)\s+bluetooth$": {
        "task_type": "single_step",
        "actions": [{"type": "system_bluetooth", "parameters": {"action": "toggle"}}],
    },
    r"^(?:airplane\s+mode)\s+(on|off)$": "airplane_mode",

    # Browser controls
    r"^(?:new\s+tab)$": {
        "task_type": "single_step",
        "actions": [{"type": "browser_new_tab", "parameters": {}}],
    },
    r"^(?:close\s+tab)$": {
        "task_type": "single_step",
        "actions": [{"type": "browser_close_tab", "parameters": {}}],
    },
    r"^(?:go\s+back|go\s+to\s+previous\s+page|back)$": {
        "task_type": "single_step",
        "actions": [{"type": "browser_back", "parameters": {}}],
    },
    r"^(?:go\s+forward|forward)$": {
        "task_type": "single_step",
        "actions": [{"type": "browser_forward", "parameters": {}}],
    },
    r"^(?:refresh|reload)$": {
        "task_type": "single_step",
        "actions": [{"type": "browser_refresh", "parameters": {}}],
    },
    r"^(?:zoom\s+in)$": {
        "task_type": "single_step",
        "actions": [{"type": "browser_zoom_in", "parameters": {}}],
    },
    r"^(?:zoom\s+out)$": {
        "task_type": "single_step",
        "actions": [{"type": "browser_zoom_out", "parameters": {}}],
    },
    r"^navigate\s+to\s+(.+)$": "navigate",
    r"^go\s+to\s+(.+)$": "navigate",

    # Media controls
    r"^(?:play|resume)$": {
        "task_type": "single_step",
        "actions": [{"type": "media_play", "parameters": {}}],
    },
    r"^pause$": {
        "task_type": "single_step",
        "actions": [{"type": "media_pause", "parameters": {}}],
    },
    r"^(?:stop)$": {
        "task_type": "single_step",
        "actions": [{"type": "media_stop", "parameters": {}}],
    },
    r"^(?:next\s+track|next\s+video|skip)$": {
        "task_type": "single_step",
        "actions": [{"type": "media_next", "parameters": {}}],
    },
    r"^(?:previous\s+track|previous\s+video|back\s+track)$": {
        "task_type": "single_step",
        "actions": [{"type": "media_previous", "parameters": {}}],
    },

    # Clipboard
    r"^copy(?:\s+(.+))?$": "copy",
    r"^paste$": {
        "task_type": "single_step",
        "actions": [{"type": "paste", "parameters": {}}],
    },
    r"^clear\s+clipboard$": {
        "task_type": "single_step",
        "actions": [{"type": "clear_clipboard", "parameters": {}}],
    },

    # Screenshots
    r"^(?:take\s+a?\s+screenshot|capture\s+screen|screenshot)$": {
        "task_type": "single_step",
        "actions": [{"type": "screenshot", "parameters": {}}],
    },

    # Time/Date
    r"^(?:what\s+time\s+is\s+it|what\s+time|current\s+time|time)$": "get_time",
    r"^(?:what\s+date\s+is\s+it|today'?s?\s+date|current\s+date|date)$": "get_date",
    r"^(?:what\s+day\s+is\s+it|what\s+day|current\s+day|day)$": "get_day",

    # Mouse/Keyboard
    r"^click(?:\s+(?:on\s+)?(.+))?$": "click",
    r"^double\s+click(?:\s+(?:on\s+)?(.+))?$": "double_click",
    r"^right\s+click(?:\s+(?:on\s+)?(.+))?$": "right_click",
    r"^scroll\s+up$": {
        "task_type": "single_step",
        "actions": [{"type": "scroll", "parameters": {"direction": "up"}}],
    },
    r"^scroll\s+down$": {
        "task_type": "single_step",
        "actions": [{"type": "scroll", "parameters": {"direction": "down"}}],
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
    
    # Check interrupt patterns first
    for pattern in INTERRUPT_PATTERNS:
        if re.match(pattern, text_lower):
            logger.info(f"Interrupt command detected")
            return {
                "task_type": "single_step",
                "actions": [{"type": "interrupt", "parameters": {}}],
            }
    
    # Try each pattern
    for pattern, handler in SIMPLE_COMMAND_RULES.items():
        match = re.match(pattern, text_lower)
        if match:
            logger.info(f"Rule matched: {pattern}")
            
            # Handler is a dict — return as-is
            if isinstance(handler, dict):
                return handler
            
            # Handler is a string reference — call appropriate handler
            if handler == "interrupt":
                return {
                    "task_type": "single_step",
                    "actions": [{"type": "interrupt", "parameters": {}}],
                }
            elif handler == "volume_level":
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
                action = match.group(1).lower()
                return {
                    "task_type": "single_step",
                    "actions": [{"type": "system_wifi", "parameters": {"action": action}}],
                }
            elif handler == "bluetooth":
                action = match.group(1).lower()
                return {
                    "task_type": "single_step",
                    "actions": [{"type": "system_bluetooth", "parameters": {"action": action}}],
                }
            elif handler == "airplane_mode":
                action = match.group(1).lower()
                return {
                    "task_type": "single_step",
                    "actions": [{"type": "system_airplane_mode", "parameters": {"action": action}}],
                }
            elif handler == "close_app":
                app_name = match.group(1).strip()
                return {
                    "task_type": "single_step",
                    "actions": [{"type": "close_app", "parameters": {"name": app_name}}],
                }
            elif handler == "navigate":
                url = match.group(1).strip()
                return {
                    "task_type": "single_step",
                    "actions": [{"type": "navigate", "parameters": {"url": url}}],
                }
            elif handler == "copy":
                text_to_copy = match.group(1).strip() if match.group(1) else ""
                return {
                    "task_type": "single_step",
                    "actions": [{"type": "copy", "parameters": {"text": text_to_copy}}],
                }
            elif handler == "get_time":
                now = datetime.now()
                time_str = now.strftime("%I:%M %p")
                return {
                    "task_type": "single_step",
                    "actions": [{"type": "speak", "parameters": {"text": f"It's {time_str}"}}],
                }
            elif handler == "get_date":
                now = datetime.now()
                date_str = now.strftime("%B %d, %Y")
                return {
                    "task_type": "single_step",
                    "actions": [{"type": "speak", "parameters": {"text": f"Today is {date_str}"}}],
                }
            elif handler == "get_day":
                now = datetime.now()
                day_str = now.strftime("%A")
                return {
                    "task_type": "single_step",
                    "actions": [{"type": "speak", "parameters": {"text": f"Today is {day_str}"}}],
                }
            elif handler == "click":
                target = match.group(1).strip() if match.group(1) else ""
                return {
                    "task_type": "single_step",
                    "actions": [{"type": "click", "parameters": {"target": target}}],
                }
            elif handler == "double_click":
                target = match.group(1).strip() if match.group(1) else ""
                return {
                    "task_type": "single_step",
                    "actions": [{"type": "double_click", "parameters": {"target": target}}],
                }
            elif handler == "right_click":
                target = match.group(1).strip() if match.group(1) else ""
                return {
                    "task_type": "single_step",
                    "actions": [{"type": "right_click", "parameters": {"target": target}}],
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
    
    if complexity_only and config.SIMPLE_COMMAND_ONLY:
        logger.warning("Complex command rejected: SIMPLE_COMMAND_ONLY=True")
        return False
    
    return True
