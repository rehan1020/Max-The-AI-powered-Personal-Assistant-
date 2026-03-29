"""Platform adapter abstract base class.

All OS-specific operations must go through a subclass of this.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Optional


class PlatformAdapter(ABC):
    """Abstract base class for all OS-specific operations."""

    @abstractmethod
    def get_volume(self) -> int:
        """Return current system volume as integer 0-100."""

    @abstractmethod
    def set_volume(self, level: int) -> bool:
        """Set system volume. level is 0-100. Return True on success."""

    @abstractmethod
    def mute(self) -> bool:
        """Mute system audio. Return True on success."""

    @abstractmethod
    def unmute(self) -> bool:
        """Unmute system audio. Return True on success."""

    @abstractmethod
    def is_muted(self) -> bool:
        """Return True if system audio is currently muted."""

    @abstractmethod
    def get_brightness(self) -> int:
        """Return current screen brightness as integer 0-100."""

    @abstractmethod
    def set_brightness(self, level: int) -> bool:
        """Set screen brightness. level is 0-100. Return True on success."""

    @abstractmethod
    def launch_app(self, name: str) -> bool:
        """Launch an application by friendly name. Return True on success."""

    @abstractmethod
    def close_app(self, name: str) -> bool:
        """Terminate an application by name. Return True on success."""

    @abstractmethod
    def list_running_apps(self) -> list[str]:
        """Return list of names of currently running applications."""

    @abstractmethod
    def install_software(self, package_name: str) -> bool:
        """Install software using the OS package manager. Return True on success."""

    @abstractmethod
    def uninstall_software(self, package_name: str) -> bool:
        """Uninstall software. Return True on success."""

    @abstractmethod
    def lock_screen(self) -> bool:
        """Lock the desktop session. Return True on success."""

    @abstractmethod
    def sleep(self) -> bool:
        """Suspend/sleep the system. Return True on success."""

    @abstractmethod
    def shutdown(self, delay_seconds: int = 60) -> bool:
        """Initiate system shutdown after delay. Return True on success."""

    @abstractmethod
    def restart(self, delay_seconds: int = 60) -> bool:
        """Initiate system restart after delay. Return True on success."""

    @abstractmethod
    def get_wifi_status(self) -> bool:
        """Return True if WiFi is enabled."""

    @abstractmethod
    def set_wifi(self, enabled: bool) -> bool:
        """Enable or disable WiFi. Return True on success."""

    @abstractmethod
    def get_bluetooth_status(self) -> bool:
        """Return True if Bluetooth is enabled."""

    @abstractmethod
    def set_bluetooth(self, enabled: bool) -> bool:
        """Enable or disable Bluetooth. Return True on success."""

    @abstractmethod
    def install_startup(self, app_path: Path) -> bool:
        """Register app to start at login. Return True on success."""

    @abstractmethod
    def remove_startup(self) -> bool:
        """Remove app from startup. Return True on success."""

    @abstractmethod
    def is_startup_enabled(self) -> bool:
        """Return True if app is registered to start at login."""

    @abstractmethod
    def send_notification(self, title: str, message: str) -> bool:
        """Send a native OS desktop notification. Return True on success."""

    @abstractmethod
    def get_clipboard(self) -> str:
        """Return current clipboard text content."""

    @abstractmethod
    def set_clipboard(self, text: str) -> bool:
        """Set clipboard text content. Return True on success."""

    @abstractmethod
    def get_battery_percent(self) -> Optional[int]:
        """Return battery percentage 0-100, or None if no battery."""

    @abstractmethod
    def get_os_name(self) -> str:
        """Return friendly OS name string."""
