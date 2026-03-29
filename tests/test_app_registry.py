"""Tests for app registry."""

import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from core.platform.app_registry import AppRegistry


class TestAppRegistry:
    """Tests for the app registry resolver."""

    @pytest.fixture
    def registry_path(self, tmp_path):
        """Create a temporary registry file."""
        registry_content = """
chrome:
  aliases: [google chrome, browser]
  windows: ["C:/Program Files/Google/Chrome/Application/chrome.exe"]
  macos: ["open", "-a", "Google Chrome"]
  linux: ["google-chrome"]

firefox:
  aliases: [mozilla firefox]
  windows: ["C:/Program Files/Mozilla Firefox/firefox.exe"]
  macos: ["open", "-a", "Firefox"]
  linux: ["firefox"]

vscode:
  aliases: [visual studio code, code editor]
  windows: ["code"]
  macos: ["open", "-a", "Visual Studio Code"]
  linux: ["code"]
"""
        registry_path = tmp_path / "app_registry.yaml"
        registry_path.write_text(registry_content)
        return registry_path

    def test_exact_match(self, registry_path):
        """Test exact name matching."""
        registry = AppRegistry(registry_path)
        
        with patch("platform.system", return_value="Windows"):
            cmd = registry.resolve("chrome")
            assert cmd is not None
            assert "chrome.exe" in cmd[0]

    def test_alias_match(self, registry_path):
        """Test alias matching."""
        registry = AppRegistry(registry_path)
        
        with patch("platform.system", return_value="Windows"):
            cmd = registry.resolve("browser")
            assert cmd is not None
            assert "chrome.exe" in cmd[0]

    def test_fuzzy_match(self, registry_path):
        """Test fuzzy matching."""
        registry = AppRegistry(registry_path)
        
        with patch("platform.system", return_value="Windows"):
            cmd = registry.resolve("vs code")
            assert cmd is not None
            assert "code" in cmd[0]

    def test_case_insensitive(self, registry_path):
        """Test case insensitive matching."""
        registry = AppRegistry(registry_path)
        
        with patch("platform.system", return_value="Windows"):
            cmd = registry.resolve("CHROME")
            assert cmd is not None

    def test_unknown_app(self, registry_path):
        """Test unknown app returns None."""
        registry = AppRegistry(registry_path)
        
        cmd = registry.resolve("nonexistent-app-12345")
        assert cmd is None
