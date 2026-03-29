"""macOS platform adapter.

Implements all platform operations for macOS 12+.
"""

import subprocess
import platform
from pathlib import Path
from typing import Optional

import psutil

from core.platform.base import PlatformAdapter


class MacOSAdapter(PlatformAdapter):
    """macOS-specific platform adapter."""

    def get_volume(self) -> int:
        try:
            result = subprocess.run(
                ["osascript", "-e", "output volume of (get volume settings)"],
                capture_output=True, text=True, timeout=5,
            )
            return int(result.stdout.strip())
        except Exception:
            return 50

    def set_volume(self, level: int) -> bool:
        try:
            subprocess.run(
                ["osascript", "-e", f"set volume output volume {level}"],
                capture_output=True, timeout=5,
            )
            return True
        except Exception:
            return False

    def mute(self) -> bool:
        try:
            subprocess.run(
                ["osascript", "-e", "set volume with output muted"],
                capture_output=True, timeout=5,
            )
            return True
        except Exception:
            return False

    def unmute(self) -> bool:
        try:
            subprocess.run(
                ["osascript", "-e", "set volume without output muted"],
                capture_output=True, timeout=5,
            )
            return True
        except Exception:
            return False

    def is_muted(self) -> bool:
        try:
            result = subprocess.run(
                ["osascript", "-e", "output muted of (get volume settings)"],
                capture_output=True, text=True, timeout=5,
            )
            return result.stdout.strip().lower() == "true"
        except Exception:
            return False

    def get_brightness(self) -> int:
        try:
            result = subprocess.run(
                ["brightness"],
                capture_output=True, text=True, timeout=5,
            )
            return int(float(result.stdout.strip()) * 100)
        except Exception:
            try:
                import screen_brightness_control as sbc
                return sbc.get_brightness()[0]
            except Exception:
                return 50

    def set_brightness(self, level: int) -> bool:
        try:
            subprocess.run(
                ["brightness", str(level / 100)],
                capture_output=True, timeout=5,
            )
            return True
        except Exception:
            try:
                import screen_brightness_control as sbc
                sbc.set_brightness(max(0, min(100, level)))
                return True
            except Exception:
                return False

    def launch_app(self, name: str) -> bool:
        try:
            subprocess.run(
                ["open", "-a", name],
                capture_output=True, timeout=10,
            )
            return True
        except Exception:
            return False

    def close_app(self, name: str) -> bool:
        try:
            subprocess.run(
                ["pkill", "-x", name],
                capture_output=True, timeout=5,
            )
            return True
        except Exception:
            return False

    def list_running_apps(self) -> list[str]:
        apps = []
        for proc in psutil.process_iter(['name']):
            try:
                apps.append(proc.info['name'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return list(set(apps))

    def install_software(self, package_name: str) -> bool:
        try:
            result = subprocess.run(
                ["brew", "install", package_name],
                capture_output=True, text=True, timeout=300,
            )
            return result.returncode == 0
        except FileNotFoundError:
            return False
        except Exception:
            return False

    def uninstall_software(self, package_name: str) -> bool:
        try:
            result = subprocess.run(
                ["brew", "uninstall", package_name],
                capture_output=True, text=True, timeout=300,
            )
            return result.returncode == 0
        except Exception:
            return False

    def lock_screen(self) -> bool:
        try:
            subprocess.run(
                ["pmset", "displaysleepnow"],
                capture_output=True, timeout=5,
            )
            return True
        except Exception:
            return False

    def sleep(self) -> bool:
        try:
            subprocess.run(
                ["pmset", "sleepnow"],
                capture_output=True, timeout=5,
            )
            return True
        except Exception:
            return False

    def shutdown(self, delay_seconds: int = 60) -> bool:
        try:
            delay_minutes = delay_seconds // 60
            subprocess.run(
                ["sudo", "shutdown", "-h", f"+{delay_minutes}"],
                capture_output=True, timeout=10,
            )
            return True
        except Exception:
            return False

    def restart(self, delay_seconds: int = 60) -> bool:
        try:
            delay_minutes = delay_seconds // 60
            subprocess.run(
                ["sudo", "shutdown", "-r", f"+{delay_minutes}"],
                capture_output=True, timeout=10,
            )
            return True
        except Exception:
            return False

    def get_wifi_status(self) -> bool:
        try:
            result = subprocess.run(
                ["networksetup", "-getairportpower", "en0"],
                capture_output=True, text=True, timeout=5,
            )
            return "On" in result.stdout
        except Exception:
            return False

    def set_wifi(self, enabled: bool) -> bool:
        try:
            state = "on" if enabled else "off"
            subprocess.run(
                ["networksetup", "-setairportpower", "en0", state],
                capture_output=True, timeout=10,
            )
            return True
        except Exception:
            return False

    def get_bluetooth_status(self) -> bool:
        try:
            result = subprocess.run(
                ["blueutil", "status"],
                capture_output=True, text=True, timeout=5,
            )
            return "On" in result.stdout
        except Exception:
            return False

    def set_bluetooth(self, enabled: bool) -> bool:
        try:
            state = "1" if enabled else "0"
            subprocess.run(
                ["blueutil", f"-{state}"],
                capture_output=True, timeout=10,
            )
            return True
        except Exception:
            return False

    def install_startup(self, app_path: Path) -> bool:
        try:
            plist_path = Path.home() / "Library/LaunchAgents/com.max.agent.plist"
            plist_path.parent.mkdir(parents=True, exist_ok=True)

            plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.max.agent</string>
    <key>ProgramArguments</key>
    <array>
        <string>{app_path}</string>
    </array>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>"""

            plist_path.write_text(plist_content)
            subprocess.run(
                ["launchctl", "load", str(plist_path)],
                capture_output=True, timeout=10,
            )
            return True
        except Exception:
            return False

    def remove_startup(self) -> bool:
        try:
            plist_path = Path.home() / "Library/LaunchAgents/com.max.agent.plist"
            if plist_path.exists():
                subprocess.run(
                    ["launchctl", "unload", str(plist_path)],
                    capture_output=True, timeout=10,
                )
                plist_path.unlink()
            return True
        except Exception:
            return False

    def is_startup_enabled(self) -> bool:
        try:
            plist_path = Path.home() / "Library/LaunchAgents/com.max.agent.plist"
            return plist_path.exists()
        except Exception:
            return False

    def send_notification(self, title: str, message: str) -> bool:
        try:
            from plyer import notification
            notification.notify(title=title, message=message, timeout=5)
            return True
        except Exception:
            return False

    def get_clipboard(self) -> str:
        try:
            result = subprocess.run(
                ["pbpaste"],
                capture_output=True, text=True, timeout=5,
            )
            return result.stdout
        except Exception:
            return ""

    def set_clipboard(self, text: str) -> bool:
        try:
            subprocess.run(
                ["pbcopy"],
                input=text,
                capture_output=True,
                timeout=5,
            )
            return True
        except Exception:
            return False

    def get_battery_percent(self) -> Optional[int]:
        try:
            battery = psutil.sensors_battery()
            if battery:
                return battery.percent
            return None
        except Exception:
            return None

    def get_os_name(self) -> str:
        result = subprocess.run(
            ["sw_vers", "-productVersion"],
            capture_output=True, text=True, timeout=5,
        )
        version = result.stdout.strip()
        return f"macOS {version}"
