"""Tests for rule parser."""

import pytest
from core.ai.rule_parser import parse_simple_command, INTERRUPT_PATTERNS


class TestRuleParser:
    """Tests for the rule-based command parser."""

    def test_interrupt_commands(self):
        """Test interrupt command patterns."""
        commands = ["stop", "cancel", "halt", "abort", "never mind", "quit"]
        for cmd in commands:
            result = parse_simple_command(cmd)
            assert result is not None
            assert result["actions"][0]["type"] == "interrupt"

    def test_volume_commands(self):
        """Test volume control commands."""
        result = parse_simple_command("mute")
        assert result is not None
        assert result["actions"][0]["type"] == "system_volume"
        assert result["actions"][0]["parameters"]["action"] == "mute"

        result = parse_simple_command("unmute")
        assert result is not None
        assert result["actions"][0]["parameters"]["action"] == "unmute"

        result = parse_simple_command("volume 50")
        assert result is not None
        assert result["actions"][0]["parameters"]["level"] == 50

        result = parse_simple_command("set volume to 75%")
        assert result is not None
        assert result["actions"][0]["parameters"]["level"] == 75

    def test_brightness_commands(self):
        """Test brightness control commands."""
        result = parse_simple_command("brightness 80")
        assert result is not None
        assert result["actions"][0]["type"] == "system_brightness"
        assert result["actions"][0]["parameters"]["level"] == 80

        result = parse_simple_command("set brightness to 50%")
        assert result is not None
        assert result["actions"][0]["parameters"]["level"] == 50

    def test_app_commands(self):
        """Test app launching commands."""
        result = parse_simple_command("open chrome")
        assert result is not None
        assert result["actions"][0]["type"] == "open_browser"

        result = parse_simple_command("open notepad")
        assert result is not None
        assert result["actions"][0]["type"] == "open_app"

        result = parse_simple_command("open calculator")
        assert result is not None
        assert result["actions"][0]["type"] == "open_app"

    def test_system_power_commands(self):
        """Test system power commands."""
        result = parse_simple_command("lock")
        assert result is not None
        assert result["actions"][0]["type"] == "system_lock"

        result = parse_simple_command("sleep")
        assert result is not None
        assert result["actions"][0]["type"] == "system_sleep"

    def test_wifi_bluetooth_commands(self):
        """Test WiFi and Bluetooth commands."""
        result = parse_simple_command("wifi on")
        assert result is not None
        assert result["actions"][0]["type"] == "system_wifi"
        assert result["actions"][0]["parameters"]["action"] == "on"

        result = parse_simple_command("wifi off")
        assert result is not None
        assert result["actions"][0]["parameters"]["action"] == "off"

        result = parse_simple_command("bluetooth on")
        assert result is not None
        assert result["actions"][0]["type"] == "system_bluetooth"

    def test_time_date_commands(self):
        """Test time and date queries."""
        result = parse_simple_command("what time is it")
        assert result is not None
        assert result["actions"][0]["type"] == "speak"

        result = parse_simple_command("what's the date")
        assert result is not None
        assert result["actions"][0]["type"] == "speak"

        result = parse_simple_command("what day is it")
        assert result is not None
        assert result["actions"][0]["type"] == "speak"

    def test_unknown_command(self):
        """Test unknown command returns None."""
        result = parse_simple_command("do something complex that requires llm")
        assert result is None
