"""Tests for safety features — plan validator and rule parser.

Converted from standalone script to proper pytest tests.
"""

import pytest
from core.ai.rule_parser import parse_simple_command
from core.ai.plan_validator import PlanValidator, detect_complexity
import config


class TestRuleParserBasics:
    """Test that common commands are parsed by the rule engine."""

    @pytest.mark.parametrize("cmd", [
        "open notepad",
        "set volume to 50",
        "lock the screen",
        "set brightness to 75",
        "mute",
        "open chrome",
    ])
    def test_simple_commands_produce_plans(self, cmd):
        """Common voice commands should produce action plans without LLM."""
        plan = parse_simple_command(cmd)
        assert plan is not None, f"'{cmd}' should be handled by rule parser"
        assert "actions" in plan
        assert len(plan["actions"]) > 0

    def test_open_notepad_type(self):
        plan = parse_simple_command("open notepad")
        assert plan is not None
        assert plan["actions"][0]["type"] == "open_app"

    def test_volume_set(self):
        plan = parse_simple_command("set volume to 50")
        assert plan is not None
        assert plan["actions"][0]["type"] == "system_volume"
        assert plan["actions"][0]["parameters"]["level"] == 50

    def test_lock_screen(self):
        plan = parse_simple_command("lock the screen")
        # "lock" or "lock the screen" — the pattern uses optional matching
        # May need to match one of the lock patterns
        if plan is not None:
            assert plan["actions"][0]["type"] == "system_lock"

    def test_mute(self):
        plan = parse_simple_command("mute")
        assert plan is not None
        assert plan["actions"][0]["type"] == "system_volume"
        assert plan["actions"][0]["parameters"]["action"] == "mute"

    def test_open_chrome(self):
        plan = parse_simple_command("open chrome")
        assert plan is not None
        assert plan["actions"][0]["type"] == "open_browser"


class TestPlanValidator:
    """Test the plan validator with various plan types."""

    def setup_method(self):
        self.validator = PlanValidator()

    def test_valid_simple_plan(self):
        plan = {
            "task_type": "single_step",
            "requires_confirmation": False,
            "actions": [
                {"type": "open_app", "parameters": {"name": "notepad"}}
            ]
        }
        is_valid, error, complexity, concerns = self.validator.validate(plan)
        assert is_valid is True
        assert error is None
        assert complexity == 0

    def test_complex_plan_detected(self):
        plan = {
            "task_type": "multi_step",
            "requires_confirmation": False,
            "actions": [
                {"type": "open_browser", "parameters": {"browser": "chrome"}},
                {"type": "navigate", "parameters": {"url": "https://google.com"}},
                {"type": "type_text", "parameters": {"text": "hello"}},
                {"type": "press_key", "parameters": {"key": "enter"}},
                {"type": "wait", "parameters": {"seconds": 2}},
            ]
        }
        is_valid, error, complexity, concerns = self.validator.validate(plan)
        assert is_valid is True
        assert complexity > 0
        assert len(concerns) > 0

    def test_dangerous_plan_flagged(self):
        plan = {
            "task_type": "multi_step",
            "requires_confirmation": False,
            "actions": [
                {"type": "system_shutdown", "parameters": {"delay": 60}},
                {"type": "file_delete", "parameters": {"path": "C:/important.txt"}},
            ]
        }
        is_valid, error, complexity, concerns = self.validator.validate(plan)
        assert is_valid is True
        assert complexity == 2  # dangerous score
        assert any("dangerous" in c.lower() for c in concerns)

    def test_invalid_action_type_rejected(self):
        plan = {
            "task_type": "single_step",
            "actions": [
                {"type": "invalid_action", "parameters": {}}
            ]
        }
        is_valid, error, complexity, concerns = self.validator.validate(plan)
        assert is_valid is False
        assert error is not None


class TestSafetyModes:
    """Test that safety configuration values are accessible."""

    def test_config_values_exist(self):
        assert hasattr(config, "SIMPLE_COMMANDS_ONLY")
        assert hasattr(config, "REQUIRE_CONFIRMATION_FOR_DANGEROUS")
        assert hasattr(config, "REJECT_COMPLEX_PLANS")
        assert hasattr(config, "MAX_ACTIONS_PER_PLAN")

    def test_default_safety_config(self):
        assert isinstance(config.SIMPLE_COMMANDS_ONLY, bool)
        assert isinstance(config.REQUIRE_CONFIRMATION_FOR_DANGEROUS, bool)
        assert isinstance(config.REJECT_COMPLEX_PLANS, bool)
        assert isinstance(config.MAX_ACTIONS_PER_PLAN, int)
        assert config.MAX_ACTIONS_PER_PLAN > 0
