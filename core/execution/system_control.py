"""System control — volume, brightness, app launching, software installation.

Uses pycaw for audio, screen_brightness_control for display,
and subprocess/winget/choco for software management.
"""

import logging
import os
import subprocess
import time
from typing import Optional

import pyautogui

import config

logger = logging.getLogger(__name__)

# Full path to PowerShell — venv can strip it from PATH
_POWERSHELL = os.path.join(
    os.environ.get("SystemRoot", r"C:\Windows"),
    "System32", "WindowsPowerShell", "v1.0", "powershell.exe",
)

# System32 path for built-in Windows tools
_SYSTEM32 = os.path.join(os.environ.get("SystemRoot", r"C:\Windows"), "System32")

# Minimal map for built-in Windows tools (these have no Start Menu shortcut)
_BUILTIN_MAP = {
    "notepad": os.path.join(_SYSTEM32, "notepad.exe"),
    "calculator": os.path.join(_SYSTEM32, "calc.exe"),
    "calc": os.path.join(_SYSTEM32, "calc.exe"),
    "file explorer": os.path.join(_SYSTEM32, "explorer.exe"),
    "explorer": os.path.join(_SYSTEM32, "explorer.exe"),
    "task manager": os.path.join(_SYSTEM32, "taskmgr.exe"),
    "cmd": os.path.join(_SYSTEM32, "cmd.exe"),
    "command prompt": os.path.join(_SYSTEM32, "cmd.exe"),
    "powershell": os.path.join(_SYSTEM32, "WindowsPowerShell", "v1.0", "powershell.exe"),
    "paint": os.path.join(_SYSTEM32, "mspaint.exe"),
    "wordpad": os.path.join(_SYSTEM32, "wordpad.exe"),
    "snipping tool": os.path.join(_SYSTEM32, "SnippingTool.exe"),
    "settings": "ms-settings:",
    "control panel": os.path.join(_SYSTEM32, "control.exe"),
}


def open_app(**params) -> dict:
    """Open an application by name — auto-discovers the executable.
    
    Search order:
      1. Built-in Windows utilities map
      2. UWP / Microsoft Store apps (Get-AppxPackage)
      3. Windows Registry (installed applications)
      4. Start Menu .lnk shortcuts
      5. PATH search (where.exe)
      6. PowerShell Start-Process fallback
    """
    name = params.get("name", "").strip()
    if not name:
        return {"success": False, "message": "No app name provided"}

    name_lower = name.lower()

    # 1) Built-in Windows tools
    if name_lower in _BUILTIN_MAP:
        exe = _BUILTIN_MAP[name_lower]
        return _launch(name, exe)

    # 2) UWP / Store apps  (WhatsApp, Telegram, etc.)
    appx_id = _find_uwp_app(name_lower)
    if appx_id:
        return _launch_uwp(name, appx_id)

    # 3) Windows Registry (installed applications)
    exe_path = _find_in_registry(name_lower)
    if exe_path:
        return _launch(name, exe_path)

    # 4) Start Menu shortcuts
    shortcut = _find_start_menu_shortcut(name_lower)
    if shortcut:
        return _launch(name, f'"{shortcut}"')

    # 5) PATH search
    exe_path = _find_on_path(name_lower)
    if exe_path:
        return _launch(name, exe_path)

    # 6) Last resort — let PowerShell try Start-Process
    return _launch_via_powershell(name)


def _launch(name: str, executable: str) -> dict:
    """Launch an executable string using os.startfile (Windows API)."""
    try:
        # os.startfile is the proper Windows way to launch applications
        # It handles .exe, .lnk, .bat, ms-* schemes, etc.
        os.startfile(executable)
        logger.info(f"Opened app: {name} → {executable}")
        return {"success": True, "message": f"Opened: {name}"}
    except Exception as e:
        logger.error(f"Failed to open '{name}' ({executable}): {e}")
        return {"success": False, "message": f"Failed to open: {name} — {e}"}


def _launch_uwp(name: str, app_id: str) -> dict:
    """Launch a UWP app via explorer shell:AppsFolder."""
    try:
        # explorer.exe shell:AppsFolder\PackageID needs subprocess with shell=True
        process = subprocess.Popen(
            f'explorer.exe shell:AppsFolder\\{app_id}',
            shell=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        # Give UWP app time to start (some apps like WhatsApp need 2-3 seconds)
        time.sleep(1)
        logger.info(f"Opened UWP app: {name} → {app_id}")
        return {"success": True, "message": f"Opened: {name}"}
    except Exception as e:
        logger.error(f"Failed to open UWP '{name}': {e}")
        return {"success": False, "message": f"Failed to open: {name} — {e}"}


def _find_in_registry(name: str) -> str | None:
    """Search Windows Registry for installed applications by name.
    
    Queries HKLM\\Software\\Microsoft\\Windows\\CurrentVersion\\Uninstall
    for any app matching the name. Returns the executable path or None.
    """
    try:
        # Use raw string for registry paths
        ps_template = (
            r'$ErrorActionPreference = "SilentlyContinue"; '
            r'$roots = @( '
            r'"HKLM:\Software\Microsoft\Windows\CurrentVersion\Uninstall", '
            r'"HKLM:\Software\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall", '
            r'"HKCU:\Software\Microsoft\Windows\CurrentVersion\Uninstall" '
            r'); '
            r'foreach ($root in $roots) { '
            r'  if (Test-Path $root) { '
            r'    Get-ItemProperty -Path "$root\*" | '
            r'    Where-Object { '
            r'      $_.DisplayName -like "*{name}*" -or $_.PSChildName -like "*{name}*" '
            r'    } | '
            r'    Select-Object -First 1 | '
            r'    ForEach-Object { '
            r'      if ($_.InstallLocation) { '
            r'        Get-ChildItem -Path $_.InstallLocation -Filter "*.exe" -ErrorAction SilentlyContinue | '
            r'        Select-Object -First 1 -ExpandProperty FullName '
            r'      } '
            r'    } '
            r'  } '
            r'}'
        )
        ps_cmd = ps_template.format(name=name)
        result = subprocess.run(
            [_POWERSHELL, "-NoProfile", "-Command", ps_cmd],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0 and result.stdout.strip():
            exe_path = result.stdout.strip().splitlines()[0]
            if exe_path and os.path.isfile(exe_path):
                logger.info(f"Found in registry: '{name}' → {exe_path}")
                return exe_path
    except Exception as e:
        logger.debug(f"Registry search failed for '{name}': {e}")
    return None


def _find_uwp_app(name: str) -> str | None:
    """Search installed UWP apps by name. Returns AppUserModelId or None."""
    try:
        # Search both package Name and display name via PowerShell
        ps_cmd = (
            f'Get-AppxPackage | Where-Object {{ '
            f'  $_.Name -like "*{name}*" -or $_.PackageFamilyName -like "*{name}*" '
            f'}} | ForEach-Object {{ '
            f'  $manifest = Get-AppxPackageManifest $_; '
            f'  $appId = $manifest.Package.Applications.Application.Id; '
            f'  if ($appId) {{ "$($_.PackageFamilyName)!$appId" }} '
            f'}}'
        )
        result = subprocess.run(
            [_POWERSHELL, "-NoProfile", "-Command", ps_cmd],
            capture_output=True, text=True, timeout=15,
        )
        if result.returncode == 0 and result.stdout.strip():
            # Return first match
            app_id = result.stdout.strip().splitlines()[0]
            if "!" in app_id:
                logger.info(f"Found UWP app '{name}' → {app_id}")
                return app_id
    except Exception as e:
        logger.debug(f"UWP search failed for '{name}': {e}")
    return None


def _find_start_menu_shortcut(name: str) -> str | None:
    """Search Start Menu folders for a matching .lnk shortcut."""
    start_menu_dirs = [
        os.path.expandvars(r"%APPDATA%\Microsoft\Windows\Start Menu\Programs"),
        r"C:\ProgramData\Microsoft\Windows\Start Menu\Programs",
    ]
    best_match = None
    for start_dir in start_menu_dirs:
        if not os.path.isdir(start_dir):
            continue
        for root, _dirs, files in os.walk(start_dir):
            for f in files:
                if not f.endswith(".lnk"):
                    continue
                f_lower = f.lower().replace(".lnk", "")
                if name in f_lower or f_lower in name:
                    full_path = os.path.join(root, f)
                    # Prefer exact match
                    if f_lower == name:
                        return full_path
                    if best_match is None:
                        best_match = full_path
    return best_match


def _find_on_path(name: str) -> str | None:
    """Search PATH for an executable."""
    for suffix in ["", ".exe", ".cmd", ".bat"]:
        try:
            result = subprocess.run(
                ["where", f"{name}{suffix}"],
                capture_output=True, text=True, timeout=3,
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip().splitlines()[0]
        except Exception:
            pass
    return None


def _launch_via_powershell(name: str) -> dict:
    """Last resort — ask PowerShell to Start-Process the name."""
    try:
        result = subprocess.run(
            [_POWERSHELL, "-NoProfile", "-Command", f'Start-Process "{name}"'],
            capture_output=True, text=True, timeout=10,
        )
        if result.returncode == 0:
            logger.info(f"Opened via Start-Process: {name}")
            return {"success": True, "message": f"Opened: {name}"}
        else:
            err = result.stderr.strip()[:200]
            logger.error(f"Start-Process failed for '{name}': {err}")
            return {"success": False, "message": f"Could not find or open: {name}"}
    except Exception as e:
        logger.error(f"PowerShell launch failed for '{name}': {e}")
        return {"success": False, "message": f"Failed to open: {name} — {e}"}


def close_app(**params) -> dict:
    """Close an application by name."""
    name = params.get("name", "").strip()
    if not name:
        return {"success": False, "message": "No app name provided"}

    try:
        # Try taskkill
        result = subprocess.run(
            ["taskkill", "/IM", f"{name}.exe", "/F"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            logger.info(f"Closed app: {name}")
            return {"success": True, "message": f"Closed: {name}"}

        # Try with partial name match
        result = subprocess.run(
            ["taskkill", "/FI", f"WINDOWTITLE eq {name}*", "/F"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        if result.returncode == 0:
            return {"success": True, "message": f"Closed: {name}"}

        return {"success": False, "message": f"Could not close: {name}"}
    except Exception as e:
        logger.error(f"Failed to close app '{name}': {e}")
        return {"success": False, "message": f"Failed to close: {name} — {e}"}


# ── Volume Control ─────────────────────────────────────────────────────────

def system_volume(**params) -> dict:
    """Control system volume. Params: level (0-100) or action (mute/unmute)."""
    try:
        from pycaw.pycaw import AudioUtilities

        # Get the default speaker device
        devices = AudioUtilities.GetSpeakers()
        
        # Modern pycaw: access volume via .EndpointVolume property
        volume = devices.EndpointVolume

        action = params.get("action", "")
        level = params.get("level")

        if action == "mute":
            volume.SetMute(1, None)
            logger.info("Volume muted")
            return {"success": True, "message": "Muted"}
        elif action == "unmute":
            volume.SetMute(0, None)
            logger.info("Volume unmuted")
            return {"success": True, "message": "Unmuted"}
        elif level is not None:
            # pycaw uses scalar 0.0 to 1.0
            scalar = max(0.0, min(1.0, int(level) / 100.0))
            volume.SetMasterVolumeLevelScalar(scalar, None)
            logger.info(f"Volume set to {level}%")
            return {"success": True, "message": f"Volume: {level}%"}
        else:
            # Get current volume
            current = volume.GetMasterVolumeLevelScalar()
            return {"success": True, "message": f"Current volume: {int(current * 100)}%"}

    except Exception as e:
        logger.error(f"Volume control failed: {e}")
        return {"success": False, "message": f"Volume control failed: {e}"}


# ── Brightness Control ─────────────────────────────────────────────────────

def system_brightness(**params) -> dict:
    """Control screen brightness. Params: level (0-100)."""
    level = params.get("level")
    if level is None:
        return {"success": False, "message": "No brightness level provided"}

    try:
        import warnings
        import screen_brightness_control as sbc
        
        # Suppress EDID parsing warnings from screen_brightness_control
        warnings.filterwarnings("ignore", category=UserWarning)
        
        level = max(0, min(100, int(level)))
        sbc.set_brightness(level)
        logger.info(f"Brightness set to {level}%")
        return {"success": True, "message": f"Brightness: {level}%"}
    except Exception as e:
        logger.error(f"Brightness control failed: {e}")
        return {"success": False, "message": f"Brightness control failed: {e}"}


# ── Software Installation ──────────────────────────────────────────────────

def install_software(**params) -> dict:
    """Install software via winget, chocolatey, or direct download.
    
    This should ONLY be called after user confirmation.
    """
    name = params.get("name", "")
    method = params.get("method", "winget").lower()
    package_id = params.get("package_id", name)

    if not name:
        return {"success": False, "message": "No software name provided"}

    try:
        if method == "winget":
            result = subprocess.run(
                ["winget", "install", "--id", package_id, "--accept-package-agreements", "--accept-source-agreements"],
                capture_output=True,
                text=True,
                timeout=300,
            )
            if result.returncode == 0:
                logger.info(f"Installed via winget: {name}")
                return {"success": True, "message": f"Installed: {name}"}
            else:
                return {"success": False, "message": f"winget failed: {result.stderr[:200]}"}

        elif method == "choco":
            result = subprocess.run(
                ["choco", "install", package_id, "-y"],
                capture_output=True,
                text=True,
                timeout=300,
            )
            if result.returncode == 0:
                logger.info(f"Installed via choco: {name}")
                return {"success": True, "message": f"Installed: {name}"}
            else:
                return {"success": False, "message": f"choco failed: {result.stderr[:200]}"}

        else:
            return {"success": False, "message": f"Unknown install method: {method}"}

    except subprocess.TimeoutExpired:
        return {"success": False, "message": f"Installation timed out: {name}"}
    except FileNotFoundError:
        return {"success": False, "message": f"{method} not found. Install it first."}
    except Exception as e:
        logger.error(f"Install failed: {e}")
        return {"success": False, "message": f"Install failed: {e}"}


# ── Extended System Controls ──────────────────────────────────────────────

def system_sleep(**params) -> dict:
    """Put the system to sleep. Params: delay (seconds, optional)."""
    delay = int(params.get("delay", 0))
    try:
        if delay > 0:
            logger.info(f"System sleep in {delay} seconds")
            time.sleep(delay)
        
        subprocess.run(["rundll32.exe", "powrprof.dll", "SetSuspendState", "0", "1", "0"], check=False)
        logger.info("System is sleeping")
        return {"success": True, "message": "System is sleeping"}
    except Exception as e:
        logger.error(f"Sleep failed: {e}")
        return {"success": False, "message": f"Sleep failed: {e}"}


def system_lock(**params) -> dict:
    """Lock the Windows screen."""
    try:
        subprocess.run(["rundll32.exe", "user32.dll", "LockWorkStation"], check=False)
        logger.info("Screen locked")
        return {"success": True, "message": "Screen locked"}
    except Exception as e:
        logger.error(f"Lock failed: {e}")
        return {"success": False, "message": f"Lock failed: {e}"}


def system_shutdown(**params) -> dict:
    """Shut down the system. Params: delay (seconds), force (bool)."""
    delay = int(params.get("delay", 60))  # Default 60 seconds
    force = params.get("force", False)
    
    try:
        if force:
            cmd = f"shutdown /s /f /t {delay}"
        else:
            cmd = f"shutdown /s /t {delay}"
        
        subprocess.run(cmd.split(), check=False)
        logger.info(f"Shutdown scheduled in {delay} seconds")
        return {"success": True, "message": f"Shutdown in {delay}s"}
    except Exception as e:
        logger.error(f"Shutdown failed: {e}")
        return {"success": False, "message": f"Shutdown failed: {e}"}


def system_restart(**params) -> dict:
    """Restart the system. Params: delay (seconds)."""
    delay = int(params.get("delay", 60))
    
    try:
        subprocess.run(f"shutdown /r /t {delay}".split(), check=False)
        logger.info(f"Restart scheduled in {delay} seconds")
        return {"success": True, "message": f"Restart in {delay}s"}
    except Exception as e:
        logger.error(f"Restart failed: {e}")
        return {"success": False, "message": f"Restart failed: {e}"}


def system_wifi(**params) -> dict:
    """Toggle WiFi on/off. Params: action (on/off/toggle)."""
    action = params.get("action", "toggle").lower()
    
    try:
        ps_cmd = (
            f'(Get-NetAdapter -Physical | Where-Object {{$_.PhysicalMediaType -eq "802.3"}}).Name | '
            f'ForEach-Object {{ '
            f'  $adapter = Get-NetAdapter -Name $_; '
            f'  if ("{action}" -eq "on") {{ Enable-NetAdapter -Name $_ -Confirm:$false }} '
            f'  elseif ("{action}" -eq "off") {{ Disable-NetAdapter -Name $_ -Confirm:$false }} '
            f'  elseif ("{action}" -eq "toggle") {{ if ($adapter.Status -eq "Up") {{ Disable-NetAdapter -Name $_ -Confirm:$false }} else {{ Enable-NetAdapter -Name $_ -Confirm:$false }} }} '
            f'}}'
        )
        
        result = subprocess.run(
            [_POWERSHELL, "-NoProfile", "-Command", ps_cmd],
            capture_output=True, text=True, timeout=10
        )
        
        logger.info(f"WiFi {action}: success")
        return {"success": True, "message": f"WiFi {action}"}
    except Exception as e:
        logger.error(f"WiFi control failed: {e}")
        return {"success": False, "message": f"WiFi control failed: {e}"}


def system_bluetooth(**params) -> dict:
    """Toggle Bluetooth on/off. Params: action (on/off/toggle)."""
    action = params.get("action", "toggle").lower()
    
    try:
        # Windows Bluetooth toggle via WMI
        ps_cmd = (
            f'$service = Get-Service bthserv; '
            f'if ("{action}" -eq "on") {{ Start-Service bthserv }} '
            f'elseif ("{action}" -eq "off") {{ Stop-Service bthserv }} '
            f'elseif ("{action}" -eq "toggle") {{ if ($service.Status -eq "Running") {{ Stop-Service bthserv }} else {{ Start-Service bthserv }} }} '
        )
        
        result = subprocess.run(
            [_POWERSHELL, "-NoProfile", "-Command", ps_cmd],
            capture_output=True, text=True, timeout=10
        )
        
        logger.info(f"Bluetooth {action}: success")
        return {"success": True, "message": f"Bluetooth {action}"}
    except Exception as e:
        logger.error(f"Bluetooth control failed: {e}")
        return {"success": False, "message": f"Bluetooth control failed: {e}"}


def system_screensaver(**params) -> dict:
    """Control screen saver. Params: action (on/off)."""
    action = params.get("action", "on").lower()
    
    try:
        if action == "on":
            subprocess.run(["rundll32.exe", "screensaver.scr", "/s"], check=False)
            logger.info("Screensaver started")
            return {"success": True, "message": "Screensaver started"}
        else:
            # Move mouse slightly to disable screensaver
            pyautogui.moveTo(pyautogui.position()[0] + 1, pyautogui.position()[1] + 1)
            logger.info("Screensaver disabled")
            return {"success": True, "message": "Screensaver disabled"}
    except Exception as e:
        logger.error(f"Screensaver control failed: {e}")
        return {"success": False, "message": f"Screensaver control failed: {e}"}


def system_mute(**params) -> dict:
    """Mute system audio."""
    try:
        from pycaw.pycaw import AudioUtilities
        devices = AudioUtilities.GetSpeakers()
        volume = devices.EndpointVolume
        volume.SetMute(1, None)
        logger.info("System muted")
        return {"success": True, "message": "System muted"}
    except Exception as e:
        logger.error(f"Mute failed: {e}")
        return {"success": False, "message": f"Mute failed: {e}"}


def system_unmute(**params) -> dict:
    """Unmute system audio."""
    try:
        from pycaw.pycaw import AudioUtilities
        devices = AudioUtilities.GetSpeakers()
        volume = devices.EndpointVolume
        volume.SetMute(0, None)
        logger.info("System unmuted")
        return {"success": True, "message": "System unmuted"}
    except Exception as e:
        logger.error(f"Unmute failed: {e}")
        return {"success": False, "message": f"Unmute failed: {e}"}
