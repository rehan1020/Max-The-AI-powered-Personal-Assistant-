"""Linux platform adapter.

Implements all platform operations for Linux (Ubuntu 20.04+, Fedora, Arch).
"""

import subprocess
import platform
from pathlib import Path
from typing import Optional

import psutil

from core.platform.base import PlatformAdapter


class LinuxAdapter(PlatformAdapter):
    """Linux-specific platform adapter."""

    def __init__(self):
        self._distro = self._detect_distro()

    def _detect_distro(self) -> str:
        """Detect the Linux distribution."""
        try:
            with open("/etc/os-release") as f:
                content = f.read()
                if "Ubuntu" in content or "Debian" in content:
                    return "debian"
                elif "Fedora" in content or "RHEL" in content or "CentOS" in content:
                    return "fedora"
                elif "Arch" in content or "Manjaro" in content:
                    return "arch"
        except Exception:
            pass
        return "debian"

    def _run(self, cmd: list, timeout: int = 10) -> bool:
        """Run a command and return success status."""
        try:
            result = subprocess.run(cmd, capture_output=True, timeout=timeout)
            return result.returncode == 0
        except Exception:
            return False

    def get_volume(self) -> int:
        try:
            result = subprocess.run(
                ["pactl", "get-sink-volume", "@DEFAULT_SINK@"],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if '%' in line:
                        volume = int(line.split('/')[-1].strip().replace('%', ''))
                        return volume
        except Exception:
            pass

        try:
            result = subprocess.run(
                ["amixer", "sget", "Master"],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if '%' in line and '[' in line:
                        volume = int(line.split('[')[1].split('%')[0])
                        return volume
        except Exception:
            pass

        return 50

    def set_volume(self, level: int) -> bool:
        level = max(0, min(100, level))
        if self._run(["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{level}%"]):
            return True
        return self._run(["amixer", "sset", "Master", f"{level}%"])

    def mute(self) -> bool:
        return self._run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "1"])

    def unmute(self) -> bool:
        return self._run(["pactl", "set-sink-mute", "@DEFAULT_SINK@", "0"])

    def is_muted(self) -> bool:
        try:
            result = subprocess.run(
                ["pactl", "get-sink-mute", "@DEFAULT_SINK@"],
                capture_output=True, text=True, timeout=5,
            )
            return "yes" in result.stdout.lower()
        except Exception:
            return False

    def get_brightness(self) -> int:
        try:
            import screen_brightness_control as sbc
            return sbc.get_brightness()[0]
        except Exception:
            try:
                result = subprocess.run(
                    ["xrandr", "--verbose"],
                    capture_output=True, text=True, timeout=5,
                )
                for line in result.stdout.split('\n'):
                    if 'Brightness:' in line:
                        return int(float(line.split(':')[1].strip()) * 100)
            except Exception:
                pass
            return 50

    def set_brightness(self, level: int) -> bool:
        level = max(0, min(100, level))
        try:
            import screen_brightness_control as sbc
            sbc.set_brightness(level)
            return True
        except Exception:
            pass

        try:
            result = subprocess.run(
                ["xrandr", "--verbose"],
                capture_output=True, text=True, timeout=5,
            )
            for line in result.stdout.split('\n'):
                if ' connected' in line:
                    output = line.split()[0]
                    subprocess.run(
                        ["xrandr", "--output", output, "--brightness", str(level / 100)],
                        capture_output=True, timeout=5,
                    )
                    return True
        except Exception:
            pass

        try:
            subprocess.run(
                ["brightnessctl", "set", f"{level}%"],
                capture_output=True, timeout=5,
            )
            return True
        except Exception:
            return False

    def launch_app(self, name: str) -> bool:
        try:
            subprocess.run(
                ["xdg-open", name],
                capture_output=True, timeout=10,
            )
            return True
        except Exception:
            pass

        try:
            subprocess.run(
                [name],
                capture_output=True, timeout=10,
            )
            return True
        except Exception:
            return False

    def close_app(self, name: str) -> bool:
        return self._run(["pkill", "-x", name])

    def list_running_apps(self) -> list[str]:
        apps = []
        for proc in psutil.process_iter(['name']):
            try:
                apps.append(proc.info['name'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
        return list(set(apps))

    def install_software(self, package_name: str) -> bool:
        if self._distro == "debian":
            if self._run(["apt-get", "install", "-y", package_name]):
                return True
            if self._run(["snap", "install", package_name]):
                return True
            return self._run(["flatpak", "install", "-y", package_name])
        elif self._distro == "fedora":
            if self._run(["dnf", "install", "-y", package_name]):
                return True
            return self._run(["flatpak", "install", "-y", package_name])
        elif self._distro == "arch":
            if self._run(["pacman", "-S", "--noconfirm", package_name]):
                return True
            return self._run(["snap", "install", package_name])
        return False

    def uninstall_software(self, package_name: str) -> bool:
        if self._distro == "debian":
            return self._run(["apt-get", "remove", "-y", package_name])
        elif self._distro == "fedora":
            return self._run(["dnf", "remove", "-y", package_name])
        elif self._distro == "arch":
            return self._run(["pacman", "-R", "--noconfirm", package_name])
        return False

    def lock_screen(self) -> bool:
        if self._run(["loginctl", "lock-session"]):
            return True
        if self._run(["xdg-screensaver", "lock"]):
            return True
        return self._run(["gnome-screensaver-command", "-l"])

    def sleep(self) -> bool:
        return self._run(["systemctl", "suspend"])

    def shutdown(self, delay_seconds: int = 60) -> bool:
        delay_minutes = delay_seconds // 60
        return self._run(["systemctl", "poweroff", f"--when=+{delay_minutes}min"])

    def restart(self, delay_seconds: int = 60) -> bool:
        delay_minutes = delay_seconds // 60
        return self._run(["systemctl", "reboot", f"--when=+{delay_minutes}min"])

    def get_wifi_status(self) -> bool:
        try:
            result = subprocess.run(
                ["nmcli", "radio", "wifi"],
                capture_output=True, text=True, timeout=5,
            )
            return "enabled" in result.stdout.lower()
        except Exception:
            return False

    def set_wifi(self, enabled: bool) -> bool:
        state = "on" if enabled else "off"
        return self._run(["nmcli", "radio", "wifi", state])

    def get_bluetooth_status(self) -> bool:
        try:
            result = subprocess.run(
                ["rfkill", "list", "bluetooth"],
                capture_output=True, text=True, timeout=5,
            )
            for line in result.stdout.split('\n'):
                if 'Soft blocked:' in line:
                    return "no" in line.lower()
        except Exception:
            pass
        return False

    def set_bluetooth(self, enabled: bool) -> bool:
        action = "unblock" if enabled else "block"
        return self._run(["rfkill", action, "bluetooth"])

    def install_startup(self, app_path: Path) -> bool:
        try:
            desktop_file = Path.home() / ".config/autostart/max-agent.desktop"
            desktop_file.parent.mkdir(parents=True, exist_ok=True)

            content = f"""[Desktop Entry]
Type=Application
Name=Max AI Agent
Exec={app_path}
X-GNOME-Autostart-enabled=true
"""

            desktop_file.write_text(content)
            return True
        except Exception:
            return False

    def remove_startup(self) -> bool:
        try:
            desktop_file = Path.home() / ".config/autostart/max-agent.desktop"
            if desktop_file.exists():
                desktop_file.unlink()
            return True
        except Exception:
            return False

    def is_startup_enabled(self) -> bool:
        try:
            desktop_file = Path.home() / ".config/autostart/max-agent.desktop"
            return desktop_file.exists()
        except Exception:
            return False

    def send_notification(self, title: str, message: str) -> bool:
        try:
            subprocess.run(
                ["notify-send", title, message],
                capture_output=True, timeout=10,
            )
            return True
        except Exception:
            try:
                from plyer import notification
                notification.notify(title=title, message=message, timeout=5)
                return True
            except Exception:
                return False

    def get_clipboard(self) -> str:
        try:
            result = subprocess.run(
                ["xclip", "-selection", "clipboard", "-o"],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0:
                return result.stdout
        except Exception:
            pass
        try:
            result = subprocess.run(
                ["xsel", "--clipboard"],
                capture_output=True, text=True, timeout=5,
            )
            if result.returncode == 0:
                return result.stdout
        except Exception:
            pass
        return ""

    def set_clipboard(self, text: str) -> bool:
        try:
            subprocess.run(
                ["xclip", "-selection", "clipboard"],
                input=text,
                capture_output=True,
                timeout=5,
            )
            return True
        except Exception:
            try:
                subprocess.run(
                    ["xsel", "--clipboard", "-i"],
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
        try:
            with open("/etc/os-release") as f:
                for line in f:
                    if line.startswith("PRETTY_NAME="):
                        return line.split("=")[1].strip().strip('"')
        except Exception:
            pass
        return f"Linux {platform.release()}"
