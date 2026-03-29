"""Tests for core subsystems — LLM provider, platform adapter, system controls.

Converted from standalone script to proper pytest tests.
Uses mocks instead of live hardware calls.
"""

import pytest
from unittest.mock import patch, MagicMock


class TestLLMProviderFactory:
    """Test LLM provider creation and configuration."""

    def test_create_cloud_provider(self):
        """Test cloud provider can be instantiated."""
        with patch.dict("os.environ", {"LLM_PROVIDER": "cloud"}):
            # Re-import to pick up env change
            import importlib
            import config
            importlib.reload(config)
            from core.ai.provider_factory import create_llm_provider
            provider = create_llm_provider()
            assert provider is not None
            assert "OpenRouter" in provider.provider_name
            provider.close()

    def test_create_local_provider(self):
        """Test local (Ollama) provider can be instantiated."""
        with patch.dict("os.environ", {"LLM_PROVIDER": "local"}):
            import importlib
            import config
            importlib.reload(config)
            from core.ai.provider_factory import create_llm_provider
            provider = create_llm_provider()
            assert provider is not None
            assert "Ollama" in provider.provider_name
            provider.close()

    def test_provider_has_plan_method(self):
        """Provider must implement plan() method."""
        from core.ai.provider_factory import create_llm_provider
        provider = create_llm_provider()
        assert hasattr(provider, "plan")
        assert callable(provider.plan)
        provider.close()


class TestVolumeControl:
    """Test volume control via mock platform adapter."""

    @patch("core.platform.get_adapter")
    def test_volume_set(self, mock_get_adapter):
        mock_adapter = MagicMock()
        mock_adapter.set_volume.return_value = True
        mock_adapter.get_volume.return_value = 50
        mock_get_adapter.return_value = mock_adapter

        from core.execution.system_control import system_volume
        result = system_volume(level=50)
        assert result["success"] is True
        mock_adapter.set_volume.assert_called_once_with(50)

    @patch("core.platform.get_adapter")
    def test_volume_mute(self, mock_get_adapter):
        mock_adapter = MagicMock()
        mock_adapter.mute.return_value = True
        mock_get_adapter.return_value = mock_adapter

        from core.execution.system_control import system_volume
        result = system_volume(action="mute")
        assert result["success"] is True
        mock_adapter.mute.assert_called_once()


class TestSystemLock:
    """Test system lock function availability."""

    def test_system_lock_function_exists(self):
        from core.execution.system_control import system_lock
        assert callable(system_lock)

    @patch("core.platform.get_adapter")
    def test_system_lock_calls_adapter(self, mock_get_adapter):
        mock_adapter = MagicMock()
        mock_adapter.lock_screen.return_value = True
        mock_get_adapter.return_value = mock_adapter

        from core.execution.system_control import system_lock
        result = system_lock()
        assert result["success"] is True
        mock_adapter.lock_screen.assert_called_once()


class TestBrightnessControl:
    """Test brightness control via mock platform adapter."""

    @patch("core.platform.get_adapter")
    def test_brightness_set(self, mock_get_adapter):
        mock_adapter = MagicMock()
        mock_adapter.set_brightness.return_value = True
        mock_get_adapter.return_value = mock_adapter

        from core.execution.system_control import system_brightness
        result = system_brightness(level=50)
        assert result["success"] is True
        mock_adapter.set_brightness.assert_called_once_with(50)


class TestPlatformAdapter:
    """Test that the platform adapter initializes correctly."""

    def test_adapter_initializes(self):
        from core.platform import get_adapter
        adapter = get_adapter()
        assert adapter is not None

    def test_adapter_has_required_methods(self):
        from core.platform import get_adapter
        adapter = get_adapter()
        required = [
            "get_volume", "set_volume", "mute", "unmute",
            "get_brightness", "set_brightness",
            "launch_app", "close_app",
            "lock_screen", "sleep", "shutdown", "restart",
            "get_os_name",
        ]
        for method_name in required:
            assert hasattr(adapter, method_name), f"Missing method: {method_name}"

    def test_get_os_name(self):
        from core.platform import get_adapter
        adapter = get_adapter()
        os_name = adapter.get_os_name()
        assert isinstance(os_name, str)
        assert len(os_name) > 0
