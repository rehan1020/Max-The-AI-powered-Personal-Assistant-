"""JSON schema validation for AI action plans."""

import json
import logging
from typing import Optional

import config

logger = logging.getLogger(__name__)


def validate_action_plan(raw_json: str) -> Optional[dict]:
    """Parse and validate an action plan from AI output.
    
    Args:
        raw_json: Raw JSON string from the AI model.
    
    Returns:
        Validated action plan dict, or None if invalid.
    """
    # Strip any markdown formatting or thinking tags the AI might add
    import re
    cleaned = raw_json.strip()
    # Remove <think>...</think> blocks from reasoning models
    cleaned = re.sub(r'<think>.*?</think>', '', cleaned, flags=re.DOTALL).strip()
    if cleaned.startswith("```json"):
        cleaned = cleaned[7:]
    if cleaned.startswith("```"):
        cleaned = cleaned[3:]
    if cleaned.endswith("```"):
        cleaned = cleaned[:-3]
    cleaned = cleaned.strip()

    # Local models sometimes emit text before/after the JSON object.
    # Extract the outermost JSON object robustly.
    cleaned = _extract_json_object(cleaned)
    if cleaned is None:
        logger.error(f"No JSON object found in AI output: {raw_json[:500]}")
        return None

    # Parse JSON
    try:
        plan = json.loads(cleaned)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON from AI: {e}\nRaw: {raw_json[:500]}")
        return None

    # Validate structure
    if not isinstance(plan, dict):
        logger.error("AI output is not a JSON object")
        return None

    # Required fields — auto-correct common local-model deviations
    if "task_type" not in plan:
        # Auto-assign based on number of actions
        if "actions" in plan and isinstance(plan["actions"], list):
            plan["task_type"] = "multi_step" if len(plan["actions"]) > 1 else "single_step"
            logger.info("Auto-assigned missing task_type")
        else:
            logger.error("Missing 'task_type' field")
            return None
    if "actions" not in plan:
        logger.error("Missing 'actions' field")
        return None

    # Validate task_type — auto-correct if invalid
    valid_task_types = {"single_step", "multi_step", "clarify"}
    if plan["task_type"] not in valid_task_types:
        num = len(plan["actions"]) if isinstance(plan.get("actions"), list) else 1
        corrected = "multi_step" if num > 1 else "single_step"
        logger.info(f"Auto-corrected task_type '{plan['task_type']}' → '{corrected}'")
        plan["task_type"] = corrected

    # Validate actions
    if not isinstance(plan["actions"], list):
        logger.error("'actions' must be a list")
        return None

    if len(plan["actions"]) == 0:
        logger.error("'actions' list is empty")
        return None

    # Validate each action
    for i, action in enumerate(plan["actions"]):
        if not isinstance(action, dict):
            logger.error(f"Action {i} is not a dict")
            return None
        if "type" not in action:
            logger.error(f"Action {i} missing 'type'")
            return None
        if action["type"] not in config.ALL_ACTION_TYPES:
            logger.error(f"Action {i} has invalid type: {action['type']}")
            return None
        if "parameters" not in action:
            # Auto-add empty parameters
            action["parameters"] = {}
        if not isinstance(action["parameters"], dict):
            logger.error(f"Action {i} 'parameters' must be a dict")
            return None

    # Ensure requires_confirmation exists
    if "requires_confirmation" not in plan:
        # Auto-detect based on action types
        plan["requires_confirmation"] = any(
            action["type"] in config.DANGEROUS_ACTIONS
            for action in plan["actions"]
        )

    logger.info(f"Valid action plan: {plan['task_type']} with {len(plan['actions'])} action(s)")
    return plan

def _extract_json_object(text: str) -> str | None:
    """Extract the first complete JSON object from *text*.

    Local LLMs sometimes prepend/append explanations.  This finds the
    first '{' … last '}' pair and returns that substring, or None.
    """
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end < start:
        return None
    return text[start:end + 1]

def plan_to_json(plan: dict) -> str:
    """Serialize a plan dict to compact JSON string."""
    return json.dumps(plan, separators=(",", ":"))
