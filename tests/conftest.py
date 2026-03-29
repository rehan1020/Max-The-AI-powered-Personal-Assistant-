"""Pytest configuration and fixtures for Max AI Agent tests."""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import MagicMock


@pytest.fixture
def mock_adapter():
    """Return a fully mocked platform adapter."""
    adapter = MagicMock()
    adapter.set_volume.return_value = True
    adapter.set_brightness.return_value = True
    adapter.launch_app.return_value = True
    adapter.mute.return_value = True
    adapter.get_os_name.return_value = "Windows 11"
    adapter.get_volume.return_value = 50
    adapter.get_brightness.return_value = 50
    adapter.lock_screen.return_value = True
    adapter.sleep.return_value = True
    adapter.shutdown.return_value = True
    adapter.restart.return_value = True
    adapter.get_wifi_status.return_value = True
    adapter.get_bluetooth_status.return_value = False
    adapter.install_startup.return_value = True
    adapter.remove_startup.return_value = True
    adapter.is_startup_enabled.return_value = False
    adapter.send_notification.return_value = True
    adapter.get_clipboard.return_value = ""
    adapter.set_clipboard.return_value = True
    adapter.get_battery_percent.return_value = 80
    return adapter


@pytest.fixture
def temp_db(tmp_path):
    """Return a path to a temporary SQLite database."""
    return tmp_path / "test_memory.db"


@pytest.fixture
def temp_cache(tmp_path):
    """Return a path to a temporary response cache."""
    return tmp_path / "test_cache.json"


@pytest.fixture
def temp_dir(tmp_path):
    """Return a temporary directory path."""
    return tmp_path / "test_app"


@pytest.fixture
def sample_config(tmp_path):
    """Create a sample config for testing."""
    config_content = """
OS=Windows
IS_WINDOWS=True
IS_MACOS=False
IS_LINUX=False
LLM_PROVIDER=local
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=phi3:mini
WHISPER_MODEL=small
WHISPER_DEVICE=cpu
"""
    env_file = tmp_path / ".env"
    env_file.write_text(config_content)
    return env_file
