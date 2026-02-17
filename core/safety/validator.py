"""Safety validator for Max action plans.

Classifies actions as SAFE or DANGEROUS, enforces protected paths,
blocks self-modification, and manages confirmation requirements.
"""

import logging
import re
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import config

logger = logging.getLogger(__name__)


# Blocked URL patterns (phishing, malware, etc.)
BLOCKED_URL_PATTERNS = [
    r"javascript:",
    r"data:",
    r"file:///",
]

# Blocked key combinations that could be destructive
BLOCKED_KEY_COMBOS = [
    # None blocked by default — but these require confirmation
]

DANGEROUS_KEY_COMBOS = [
    "alt+f4",
    "ctrl+alt+delete",
    "ctrl+shift+delete",
    "win+l",
]


class SafetyValidator:
    """Validates action plans for safety before execution."""

    def __init__(self):
        self.protected_paths = [Path(p).resolve() for p in config.PROTECTED_PATHS]
        self.safe_mode = True  # When True, ALL dangerous actions require confirmation
        logger.info(f"Safety validator initialized. Protected paths: {len(self.protected_paths)}")

    def classify_action(self, action: dict) -> str:
        """Classify a single action as 'safe' or 'dangerous'.
        
        Returns: 'safe', 'dangerous', or 'blocked'
        """
        action_type = action.get("type", "")
        params = action.get("parameters", {})

        # Check if action type is even allowed
        if action_type not in config.ALL_ACTION_TYPES:
            return "blocked"

        # ── Path Safety ──
        for key in ("path", "source", "destination"):
            if key in params:
                path_check = self._check_path_safety(params[key])
                if path_check == "blocked":
                    return "blocked"
                if path_check == "dangerous":
                    return "dangerous"

        # ── URL Safety ──
        if "url" in params:
            url_check = self._check_url_safety(params["url"])
            if url_check == "blocked":
                return "blocked"

        # ── Key Safety ──
        if action_type == "press_key" and "key" in params:
            key_check = self._check_key_safety(params["key"])
            if key_check != "safe":
                return key_check

        # ── Action Type Classification ──
        if action_type in config.DANGEROUS_ACTIONS:
            return "dangerous"

        return "safe"

    def validate_plan(self, plan: dict) -> dict:
        """Validate an entire action plan.
        
        Returns a dict with:
            - 'approved': bool — True if plan can proceed
            - 'needs_confirmation': bool — True if user must confirm
            - 'blocked_actions': list of blocked action indices
            - 'dangerous_actions': list of dangerous action indices
            - 'reasons': list of human-readable reason strings
        """
        result = {
            "approved": True,
            "needs_confirmation": plan.get("requires_confirmation", False),
            "blocked_actions": [],
            "dangerous_actions": [],
            "safe_actions": [],
            "reasons": [],
        }

        for i, action in enumerate(plan.get("actions", [])):
            classification = self.classify_action(action)

            if classification == "blocked":
                result["blocked_actions"].append(i)
                result["reasons"].append(
                    f"Action {i+1} ({action['type']}) is BLOCKED: "
                    f"violates safety policy"
                )
            elif classification == "dangerous":
                result["dangerous_actions"].append(i)
                result["needs_confirmation"] = True
                result["reasons"].append(
                    f"Action {i+1} ({action['type']}) requires confirmation"
                )
            else:
                result["safe_actions"].append(i)

        # If any actions are blocked, the whole plan is blocked
        if result["blocked_actions"]:
            result["approved"] = False

        # In safe mode, dangerous actions always need confirmation
        if self.safe_mode and result["dangerous_actions"]:
            result["needs_confirmation"] = True

        return result

    def _check_path_safety(self, path_str: str) -> str:
        """Check if a file path is safe to operate on.
        
        Returns: 'safe', 'dangerous', or 'blocked'
        """
        try:
            path = Path(path_str).resolve()
        except Exception:
            return "blocked"

        # Check against protected paths
        for protected in self.protected_paths:
            try:
                path.relative_to(protected)
                logger.warning(f"Path blocked (protected): {path_str}")
                return "blocked"
            except ValueError:
                continue  # Not inside this protected path

        # Check for suspicious patterns
        suspicious_dirs = ["system32", "syswow64", "boot", "recovery"]
        for part in path.parts:
            if part.lower() in suspicious_dirs:
                return "dangerous"

        return "safe"

    def _check_url_safety(self, url: str) -> str:
        """Check if a URL is safe to navigate to.
        
        Returns: 'safe' or 'blocked'
        """
        url_lower = url.lower().strip()

        for pattern in BLOCKED_URL_PATTERNS:
            if re.match(pattern, url_lower):
                logger.warning(f"URL blocked (pattern match): {url}")
                return "blocked"

        try:
            parsed = urlparse(url)
            if not parsed.scheme:
                # Assume https
                return "safe"
            if parsed.scheme not in ("http", "https"):
                logger.warning(f"URL blocked (scheme): {url}")
                return "blocked"
        except Exception:
            return "blocked"

        return "safe"

    def _check_key_safety(self, key_combo: str) -> str:
        """Check if a key combination is safe.
        
        Returns: 'safe', 'dangerous', or 'blocked'
        """
        normalized = key_combo.lower().replace(" ", "")

        for blocked in BLOCKED_KEY_COMBOS:
            if normalized == blocked.replace(" ", ""):
                return "blocked"

        for dangerous in DANGEROUS_KEY_COMBOS:
            if normalized == dangerous.replace(" ", ""):
                return "dangerous"

        return "safe"

    def format_confirmation_message(self, plan: dict, validation: dict) -> str:
        """Generate a human-readable confirmation message."""
        lines = ["⚠️ The following actions require your approval:\n"]

        for i in validation["dangerous_actions"]:
            action = plan["actions"][i]
            action_type = action["type"]
            params = action.get("parameters", {})
            desc = self._describe_action(action_type, params)
            lines.append(f"  • {desc}")

        if validation["blocked_actions"]:
            lines.append("\n🚫 The following actions were BLOCKED:")
            for i in validation["blocked_actions"]:
                action = plan["actions"][i]
                lines.append(f"  • {action['type']} — violates safety policy")

        lines.append("\nDo you want to proceed?")
        return "\n".join(lines)

    def _describe_action(self, action_type: str, params: dict) -> str:
        """Generate human-readable description of an action."""
        descriptions = {
            "file_delete": f"Delete file: {params.get('path', 'unknown')}",
            "file_move": f"Move file from {params.get('source', '?')} to {params.get('destination', '?')}",
            "install_software": f"Install: {params.get('name', 'unknown')} via {params.get('method', 'unknown')}",
            "system_volume": f"Change volume to {params.get('level', params.get('action', '?'))}",
            "system_brightness": f"Change brightness to {params.get('level', '?')}",
            "press_key": f"Press key: {params.get('key', '?')}",
        }
        return descriptions.get(action_type, f"{action_type}: {params}")
