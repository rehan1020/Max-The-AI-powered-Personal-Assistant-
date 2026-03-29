import os
import shutil
import subprocess
import time
from pathlib import Path
from typing import Optional

import psutil

from core.platform.base import PlatformAdapter


class WindowsAdapter(PlatformAdapter):
    """Windows-specific platform adapter."""

    def __init__(self):
        self._po_shell = None

    def _get_powershell(self) -> str:
        """Get PowerShell executable path."""
        return os.path.join(
            os.environ.get("SystemRoot", r"C:\Windows"),
            "System32", "WindowsPowerShell", "v1.0", "powershell.exe",
        )

    def _find_executable(self, name: str) -> Optional[str]:
        """Dynamically discover an executable on the system.

        Search order:
        1. shutil.which() — checks PATH
        2. Windows App Paths registry
        3. Returns None if not found (caller uses os.startfile/Start-Process)
        """
        # 1. PATH lookup
        found = shutil.which(name)
        if found:
            return found

        # Also check common exe variants
        if not name.endswith(".exe"):
            found = shutil.which(name + ".exe")
            if found:
                return found

        # 2. App Paths registry
        try:
            import winreg
            key_path = rf"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\{name}"
            if not name.endswith(".exe"):
                key_path += ".exe"
            key = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path)
            path, _ = winreg.QueryValueEx(key, "")
            winreg.CloseKey(key)
            if path and Path(path).exists():
                return path
        except (OSError, FileNotFoundError, ImportError):
            pass

        return None

    def get_volume(self) -> int:
        try:
            from pycaw.pycaw import AudioUtilities
            devices = AudioUtilities.GetSpeakers()
            volume = devices.EndpointVolume
            return int(volume.GetMasterVolumeLevelScalar() * 100)
        except Exception:
            return 50

    def set_volume(self, level: int) -> bool:
        try:
            from pycaw.pycaw import AudioUtilities
            devices = AudioUtilities.GetSpeakers()
            volume = devices.EndpointVolume
            scalar = max(0.0, min(1.0, level / 100.0))
            volume.SetMasterVolumeLevelScalar(scalar, None)
            return True
        except Exception:
            return False

    def mute(self) -> bool:
        try:
            from pycaw.pycaw import AudioUtilities
            devices = AudioUtilities.GetSpeakers()
            volume = devices.EndpointVolume
            volume.SetMute(1, None)
            return True
        except Exception:
            return False

    def unmute(self) -> bool:
        try:
            from pycaw.pycaw import AudioUtilities
            devices = AudioUtilities.GetSpeakers()
            volume = devices.EndpointVolume
            volume.SetMute(0, None)
            return True
        except Exception:
            return False

    def is_muted(self) -> bool:
        try:
            from pycaw.pycaw import AudioUtilities
            devices = AudioUtilities.GetSpeakers()
            volume = devices.EndpointVolume
            return volume.GetMute()
        except Exception:
            return False

    def get_brightness(self) -> int:
        try:
            import screen_brightness_control as sbc
            return sbc.get_brightness()[0]
        except Exception:
            return 50

    def set_brightness(self, level: int) -> bool:
        try:
            import screen_brightness_control as sbc
            sbc.set_brightness(max(0, min(100, level)))
            return True
        except Exception:
            return False

    def launch_app(self, name: str) -> bool:
        try:
            name_lower = name.lower()

            # Try to find the executable dynamically
            exe_path = self._find_executable(name_lower)
            if exe_path:
                os.startfile(exe_path)
                return True

            # Try os.startfile directly (handles UWP apps, shell URIs, etc.)
            try:
                os.startfile(name)
                return True
            except OSError:
                pass

            # Last resort: PowerShell Start-Process
            result = subprocess.run(
                [self._get_powershell(), "-NoProfile", "-Command", f'Start-Process "{name}"'],
                capture_output=True, text=True, timeout=10,
            )
            return result.returncode == 0
        except Exception:
            return False

    def close_app(self, name: str) -> bool:
        try:
            result = subprocess.run(
                ["taskkill", "/IM", f"{name}.exe", "/F"],
                capture_output=True, text=True, timeout=5,
            )
            return result.returncode == 0
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
                ["winget", "install", "--id", package_name, "--accept-package-agreements", "--accept-source-agreements"],
                capture_output=True, text=True, timeout=300,
            )
            if result.returncode != 0:
                result = subprocess.run(
                    ["choco", "install", package_name, "-y"],
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
                ["winget", "uninstall", "--id", package_name],
                capture_output=True, text=True, timeout=300,
            )
            return result.returncode == 0
        except Exception:
            return False

    def lock_screen(self) -> bool:
        try:
            import ctypes
            ctypes.windll.user32.LockWorkStation()
            return True
        except Exception:
            return False

    def sleep(self) -> bool:
        try:
            subprocess.run(
                ["rundll32.exe", "powrprof.dll", "SetSuspendState", "0", "1", "0"],
                check=False
            )
            return True
        except Exception:
            return False

    def shutdown(self, delay_seconds: int = 60) -> bool:
        try:
            subprocess.run(
                ["shutdown", "/s", "/t", str(delay_seconds)],
                check=False
            )
            return True
        except Exception:
            return False

    def restart(self, delay_seconds: int = 60) -> bool:
        try:
            subprocess.run(
                ["shutdown", "/r", "/t", str(delay_seconds)],
                check=False
            )
            return True
        except Exception:
            return False

    def get_wifi_status(self) -> bool:
        try:
            result = subprocess.run(
                ["netsh", "wlan", "show", "interfaces"],
                capture_output=True, text=True, timeout=10,
            )
            return "connected" in result.stdout.lower()
        except Exception:
            return False

    def set_wifi(self, enabled: bool) -> bool:
        try:
            action = "enable" if enabled else "disable"
            subprocess.run(
                ["netsh", "interface", "set", "interface", "Wi-Fi", action],
                capture_output=True, text=True, timeout=10,
            )
            return True
        except Exception:
            return False

    def get_bluetooth_status(self) -> bool:
        try:
            result = subprocess.run(
                ["powershell", "-Command", "Get-Service bthserv"],
                capture_output=True, text=True, timeout=10,
            )
            return "Running" in result.stdout
        except Exception:
            return False

    def set_bluetooth(self, enabled: bool) -> bool:
        try:
            action = "Start-Service" if enabled else "Stop-Service"
            subprocess.run(
                ["powershell", "-Command", f"{action} bthserv"],
                capture_output=True, text=True, timeout=10,
            )
            return True
        except Exception:
            return False

    def install_startup(self, app_path: Path) -> bool:
        try:
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                key_path,
                0,
                winreg.KEY_SET_VALUE,
            )
            command = f'"{app_path}"'
            winreg.SetValueEx(key, "MaxAIAgent", 0, winreg.REG_SZ, command)
            winreg.CloseKey(key)
            return True
        except Exception:
            return False

    def remove_startup(self) -> bool:
        try:
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(
                winreg.HKEY_CURRENT_USER,
                key_path,
                0,
                winreg.KEY_SET_VALUE,
            )
            try:
                winreg.DeleteValue(key, "MaxAIAgent")
            except FileNotFoundError:
                pass
            winreg.CloseKey(key)
            return True
        except Exception:
            return False

    def is_startup_enabled(self) -> bool:
        try:
            import winreg
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
            try:
                winreg.QueryValueEx(key, "MaxAIAgent")
                winreg.CloseKey(key)
                return True
            except FileNotFoundError:
                winreg.CloseKey(key)
                return False
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
            import pyperclip
            return pyperclip.paste()
        except Exception:
            return ""

    def set_clipboard(self, text: str) -> bool:
        try:
            import pyperclip
            pyperclip.copy(text)
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
        import platform
        return f"Windows {platform.release()}"
