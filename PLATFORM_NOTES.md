# Platform-Specific Notes

This document covers platform-specific limitations and requirements for Max AI Agent.

## Windows

- **Brightness Control**: Uses `screen-brightness-control` library
- **Volume Control**: Uses `pycaw` library (requires Windows Audio API)
- **App Launching**: Supports Windows Store (UWP) apps via PowerShell
- **Startup**: Uses Windows Registry or Start Menu shortcuts

## macOS

- **Brightness Control**: Requires `brightness` CLI tool
  - Install with: `brew install brightness`
- **Volume Control**: Uses `osascript` (AppleScript)
- **Bluetooth Control**: Requires `blueutil` CLI tool
  - Install with: `brew install blueutil`
- **Startup**: Uses LaunchAgents plist file
- **Notifications**: Uses native macOS notification center via `plyer`

## Linux

### Ubuntu/Debian

- **Brightness Control**: Uses `xrandr` for X11, or `brightnessctl` for Wayland
- **Volume Control**: Uses PulseAudio (`pactl`) or ALSA (`amixer`)
- **Notifications**: Uses `notify-send` or `plyer`
- **Clipboard**: Uses `xclip` or `xsel` (X11), `wl-clipboard` (Wayland)

### Fedora/RHEL

- Same as Ubuntu/Debian but uses `dnf` for package management

### Arch Linux

- Same as Ubuntu/Debian but uses `pacman` for package management

### Wayland Specific

- Some mouse/keyboard automation may require `ydotool` instead of `xdotool`
- Screen brightness may require `brightnessctl`
- Clipboard requires `wl-clipboard`

## Common Requirements

### System Dependencies

| Dependency | Windows | macOS | Linux |
|------------|---------|-------|-------|
| Python | 3.11+ | 3.11+ | 3.11+ |
| Chrome/Chromium | Required | Required | Required |
| Audio drivers | Built-in | Built-in | ALSA/PulseAudio |

### Optional Dependencies

| Tool | Purpose | Install Command |
|------|---------|-----------------|
| Ollama | Local LLM | See [ollama.ai](https://ollama.ai) |
| Playwright | Browser automation | `playwright install chromium` |

## Troubleshooting

### Microphone Not Detected

1. Check system permissions for microphone access
2. On Windows: Settings > Privacy > Microphone
3. On macOS: System Preferences > Security & Privacy > Privacy > Microphone
4. On Linux: Check PulseAudio/PipeWire configuration

### Chrome Not Launching

1. Verify Chrome is installed in the default location
2. Or set `CHROME_PATH` in `.env` to the correct path

### Voice Commands Not Working

1. Check microphone is selected in system settings
2. Verify audio input device is not muted
3. Check `WHISPER_MODEL` and `WHISPER_DEVICE` in `.env`

### System Controls Not Working

- Some system controls require administrator/root privileges
- On Linux, some commands require `sudo` (not supported by Max)
