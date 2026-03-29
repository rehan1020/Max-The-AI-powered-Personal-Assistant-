# 🌍 Multi-Platform Notes

> [!WARNING]
> **Linux and macOS support is currently in BETA / EXPERIMENTAL.**
> These platforms have not been as extensively tested as Windows. Expect bugs and please report them!

## 🪟 Windows (Stable)

- **Brightness**: Uses `screen-brightness-control`.
- **Volume**: Uses `pycaw`.
- **App Management**: Supports Win32 and UWP (Windows Store) apps via PowerShell.
- **Startup**: Managed via the Windows Registry.

## 🍎 macOS (Beta - MacBooks)

- **Requirement**: Desktop automation on macOS requires `Accessibility` and `Microphone` permissions.
- **Brightness**: Requires `brightness` CLI (`brew install brightness`).
- **Volume**: Native control via `osascript` (AppleScript).
- **Bluetooth**: Requires `blueutil` (`brew install blueutil`).
- **Package Manager**: Supports `Homebrew` for software installation commands.
- **Startup**: Uses `LaunchAgents` plist files.
- **Clipboard**: Native `pbcopy` and `pbpaste`.

## 🐧 Linux (Experimental)

### Requirements
Max assumes a standard desktop environment (GNOME, KDE, etc.) with the following tools installed:
- **Audio**: `pulseaudio-utils` (for `pactl`) or `alsa-utils`.
- **Network**: `NetworkManager` (for `nmcli`).
- **Notifications**: `libnotify-bin` (for `notify-send`).
- **Clipboard**: `xclip` or `xsel`.

### Wayland Support
For modern distros using Wayland (e.g., Ubuntu 22.04+ default):
- Brightness requires `brightnessctl`.
- Clipboard requires `wl-clipboard`.
- Global hotkeys and mouse automation may have limited functionality compared to X11.

---

## 📋 Dependency Comparison

| Feature | Windows | macOS | Linux |
|---------|---------|-------|-------|
| **Volume** | `pycaw` | `osascript` | `pactl` / `amixer` |
| **Brightness** | `sbc` | `brightness` (brew) | `xrandr` / `brightnessctl` |
| **WiFi** | Native | `networksetup` | `nmcli` |
| **Bluetooth** | Native | `blueutil` (brew) | `rfkill` |
| **Apps** | PowerShell/Registry| `open` / `pkill` | `xdg-open` / `pkill` |
| **Install** | `winget` | `brew` | `apt` / `dnf` / `pacman` |

---

## 🛠️ Troubleshooting

### macOS Permission Issues
If Max fails to type or click on macOS:
1. Go to **System Settings** > **Privacy & Security**.
2. Under **Accessibility**, ensure your terminal (or Python) is allowed.
3. Under **Microphone**, ensure access is granted.

### Linux Audio (No Sound)
1. Ensure your user is in the `audio` group: `sudo usermod -aG audio $USER`.
2. Verify `pactl info` runs without errors in your terminal.

### Screen Capture Black Screen
- On **Wayland (Linux)**, standard screen capture might return a black screen for security reasons. You may need to switch to an X11 session or configure PipeWire sharing.
- On **macOS**, ensure "Screen Recording" permission is granted in System Settings.
