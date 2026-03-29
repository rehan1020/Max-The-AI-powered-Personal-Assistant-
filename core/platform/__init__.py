"""Platform adapter factory.

Detects the OS at import time and returns the correct adapter.
"""

import platform
import sys

_adapter = None


def get_adapter():
    """Get the platform adapter for the current OS.
    
    Returns:
        PlatformAdapter: The platform-specific adapter for the current OS.
    
    Raises:
        RuntimeError: If the operating system is not supported.
    """
    global _adapter
    if _adapter is not None:
        return _adapter

    os_name = platform.system()

    if os_name == "Windows":
        from core.platform.windows_adapter import WindowsAdapter
        _adapter = WindowsAdapter()
    elif os_name == "Darwin":
        from core.platform.macos_adapter import MacOSAdapter
        _adapter = MacOSAdapter()
    elif os_name == "Linux":
        from core.platform.linux_adapter import LinuxAdapter
        _adapter = LinuxAdapter()
    else:
        raise RuntimeError(f"Unsupported operating system: {os_name}")

    return _adapter


__all__ = ["get_adapter", "PlatformAdapter"]
