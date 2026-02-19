"""JSON Schema validation and plan verification.

Ensures that LLM-generated action plans conform to allowed structure.
Detects complexity and validates action safety.
"""

import json
import logging
from typing import Optional, List, Dict, Any

logger = logging.getLogger(__name__)

# Allowed action types
ALLOWED_ACTIONS = {
    "open_app",
    "close_app",
    "open_browser",
    "navigate",
    "click",
    "type_text",
    "press_key",
    "move_mouse",
    "file_create",
    "file_delete",
    "file_move",
    "install_software",
    "system_volume",
    "system_brightness",
    "system_sleep",
    "system_lock",
    "system_shutdown",
    "system_restart",
    "system_wifi",
    "system_bluetooth",
    "system_screensaver",
    "system_mute",
    "system_unmute",
    "summarize_screen",
    "read_screen",
    "search_web",
    "wait",
}

# Actions that require confirmation
DANGEROUS_ACTIONS = {
    "install_software",
    "file_delete",
    "system_shutdown",
    "system_restart",
    "system_sleep",
}

# Dangerous parameters that should always require confirmation
DANGEROUS_PATTERNS = {
    "file_delete": ["path"],
    "install_software": ["name"],
    "system_shutdown": ["delay"],
}


def validate_plan_schema(plan: dict) -> tuple[bool, Optional[str]]:
    """Validate that a plan conforms to the expected schema.
    
    Args:
        plan: Action plan dict from LLM
        
    Returns:
        (is_valid, error_message)
    """
    if not isinstance(plan, dict):
        return False, "Plan must be a dict"
    
    # Check required fields
    if "task_type" not in plan:
        return False, "Missing required field: task_type"
    
    if "actions" not in plan:
        return False, "Missing required field: actions"
    
    # Validate task_type
    if plan.get("task_type") not in ["single_step", "multi_step", "clarify"]:
        return False, f"Invalid task_type: {plan.get('task_type')}"
    
    # Validate actions
    if not isinstance(plan.get("actions"), list):
        return False, "actions must be a list"
    
    if not plan.get("actions"):
        return False, "actions list cannot be empty"
    
    # Validate each action
    for i, action in enumerate(plan.get("actions", [])):
        if not isinstance(action, dict):
            return False, f"Action {i} must be a dict"
        
        if "type" not in action:
            return False, f"Action {i} missing 'type' field"
        
        action_type = action.get("type")
        if action_type not in ALLOWED_ACTIONS:
            return False, f"Action {i} has invalid type: {action_type}"
        
        if "parameters" not in action:
            return False, f"Action {i} missing 'parameters' field"
        
        if not isinstance(action.get("parameters"), dict):
            return False, f"Action {i} parameters must be a dict"
    
    return True, None


def detect_complexity(plan: dict) -> tuple[int, List[str]]:
    """Detect complexity level and issues in a plan.
    
    Returns:
        (complexity_score, list_of_concerns)
        
        Score: 0=simple, 1=moderate, 2=complex
        Concerns: List of detected complexity issues
    """
    concerns = []
    score = 0
    
    actions = plan.get("actions", [])
    
    # Multi-step is more complex
    if len(actions) > 1:
        concerns.append(f"Multiple actions ({len(actions)})")
        score = 1
    
    # Check for dangerous actions
    dangerous = [
        a for a in actions 
        if a.get("type") in DANGEROUS_ACTIONS
    ]
    if dangerous:
        concerns.append(f"Contains {len(dangerous)} dangerous action(s)")
        score = max(score, 2)
    
    # Check for conditional logic patterns (future-proofing)
    plan_str = json.dumps(plan).lower()
    if any(word in plan_str for word in ["if", "else", "conditional", "condition"]):
        concerns.append("Contains conditional logic")
        score = 2
    
    # Check for loops/repeat patterns
    if "wait" in [a.get("type") for a in actions]:
        if len(actions) > 2:
            concerns.append("Long sequence with waits (potential loop)")
            score = 2
    
    return score, concerns


def requires_confirmation(plan: dict) -> bool:
    """Determine if plan requires user confirmation before execution.
    
    Args:
        plan: Action plan dict
        
    Returns:
        True if requires confirmation
    """
    # Check if plan says it requires confirmation
    if plan.get("requires_confirmation"):
        return True
    
    # Check for dangerous actions
    for action in plan.get("actions", []):
        if action.get("type") in DANGEROUS_ACTIONS:
            return True
    
    return False


def sanitize_action_parameters(action_type: str, params: dict) -> dict:
    """Sanitize parameters for dangerous actions.
    
    Removes or validates suspicious parameters.
    
    Args:
        action_type: Type of action
        params: Parameters dict
        
    Returns:
        Sanitized parameters dict
    """
    safe_params = params.copy()
    
    # File delete: ensure path is valid
    if action_type == "file_delete":
        path = safe_params.get("path", "")
        if not path or path in ["/", "C:\\", "C:"]:
            logger.warning("Blocked dangerous file delete path")
            return {}
    
    # Install software: validate package_id doesn't contain shell metacharacters
    if action_type == "install_software":
        pkg_id = safe_params.get("package_id", "")
        if any(char in pkg_id for char in [";", "|", "&", ">", "<", "`"]):
            logger.warning("Blocked suspicious characters in package_id")
            safe_params["package_id"] = ""
    
    # Shutdown/Restart: cap delay to reasonable value (max 1 hour)
    if action_type in ["system_shutdown", "system_restart"]:
        delay = safe_params.get("delay", 60)
        if delay > 3600:
            logger.warning(f"Capped shutdown delay from {delay}s to 3600s")
            safe_params["delay"] = 3600
    
    return safe_params


class PlanValidator:
    """Orchestrated plan validation combining schema, complexity, and safety checks."""
    
    def __init__(self, strict_mode: bool = False):
        """
        Args:
            strict_mode: If True, reject any complex plans
        """
        self.strict_mode = strict_mode
    
    def validate(self, plan: dict) -> tuple[bool, Optional[str], int, List[str]]:
        """Full validation of an action plan.
        
        Returns:
            (is_valid, error_message, complexity_score, concerns)
        """
        # Check schema first
        is_schema_valid, schema_error = validate_plan_schema(plan)
        if not is_schema_valid:
            return False, schema_error, 0, []
        
        # Check complexity
        complexity, concerns = detect_complexity(plan)
        
        if self.strict_mode and complexity > 0:
            return False, "Complex plans rejected in strict mode", complexity, concerns
        
        return True, None, complexity, concerns
    
    def sanitize_plan(self, plan: dict) -> dict:
        """Sanitize all actions in a plan.
        
        Args:
            plan: Original plan
            
        Returns:
            Sanitized plan
        """
        safe_plan = plan.copy()
        safe_actions = []
        
        for action in plan.get("actions", []):
            safe_action = action.copy()
            safe_action["parameters"] = sanitize_action_parameters(
                action.get("type"), 
                action.get("parameters", {})
            )
            safe_actions.append(safe_action)
        
        safe_plan["actions"] = safe_actions
        return safe_plan
