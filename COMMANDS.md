# Max Voice Commands Guide

Max now understands natural voice commands. The LLM model dynamically discovers and launches apps without hardcoding. Here are proper command examples:

## Opening Apps

**WhatsApp:**
- "Open WhatsApp"
- "Launch WhatsApp"
- "Start WhatsApp"

**Chrome / Firefox / Edge:**
- "Open Chrome" (or Firefox, Edge, etc.)
- "Launch Chrome"
- "Start the browser"

**Discord:**
- "Open Discord"
- "Launch Discord"

**Spotify, Telegram, VS Code, Git, etc.:**
- "Open Spotify"
- "Launch Telegram"
- "Open Visual Studio Code"
- "Open Git Bash"

**Windows Built-in Apps:**
- "Open Calculator"
- "Open Notepad"
- "Open Task Manager"
- "Open Settings"
- "Open File Explorer"
- "Open Control Panel"

## Web Navigation & Browsing

**Search Google:**
- "Search for weather" → Opens browser + searches Google
- "Search for Python tutorials"
- "Look up machine learning"

**Open Websites:**
- "Open Amazon" (Max will open browser + navigate to amazon.com)
- "Go to YouTube"
- "Open Gmail"
- "Visit Reddit"

**Play Music on Amazon Music:**
- "Open Amazon Music"
- "Launch Amazon Music"

Then say:
- "Search for jazz music" (to search within Amazon Music)
- "Play my playlist" (depends on Amazon Music UI - voice commands vary by app)

**Note:** Voice commands within apps (like "play this song") depend on the app's voice interface. Max can:
1. ✅ Open the app for you
2. ❌ Cannot control rich audio interfaces directly (Amazon Music, Spotify must be controlled via their built-in voice or UI)

For Spotify specifically:
- "Open Spotify" → Max opens Spotify
- Then use Spotify's voice command or UI to play songs

## System Controls

**Volume:**
- "Set volume to 50"
- "Lower the volume"
- "Increase volume"
- "Mute"
- "Unmute"

**Brightness:**
- "Set brightness to 75"
- "Lower brightness"
- "Increase brightness"
- "Make it brighter"

**Power Management:**
- "Sleep" (put system to sleep)
- "Lock the screen" (lock Windows)
- "Shutdown" (shutdown in 60 seconds)
- "Restart" (restart in 60 seconds)
- "Restart in 30 seconds"

**Connectivity:**
- "Turn WiFi on" / "Turn WiFi off" / "Toggle WiFi"
- "Turn Bluetooth on" / "Turn Bluetooth off" / "Toggle Bluetooth"

**Other System Tasks:**
- "Start screensaver"
- "Turn off screensaver"

## File Operations

**Create Files:**
- "Create a file called notes.txt with content 'Fix the bug'"
- "Create a new document at ~/Desktop/test.txt"

**Delete Files:**
- "Delete the file ~/Desktop/old.txt"

**Move Files:**
- "Move ~/Downloads/photo.jpg to ~/Pictures/"

## Clipboard Operations

**Copy to Clipboard:**
- "Copy 'hello world' to clipboard"
- "Copy the text 'Meeting at 5' to my clipboard"
- "Put 'Draft 1' on the clipboard"

**Paste from Clipboard:**
- "Paste from clipboard" (Note: Max will simulate Ctrl+V)

**Clear Clipboard:**
- "Clear the clipboard"
- "Wipe my clipboard"

## Notifications & Battery

**Check Battery:**
- "What's my battery level?"
- "Check battery status"
- "How much battery is left?"

**Send Notifications:**
- "Notify me when finished"
- "Send a notification saying 'Task Completed'"
- "Alert me with 'Dinner is ready'"

## Startup & Installation

**Auto-Startup:**
- "Enable auto-startup" (Adds Max to Windows startup)
- "Disable auto-startup"
- "Check if startup is enabled"

**Software Installation:**
- "Install Visual Studio Code"
- "Install Google Chrome"
- "Install VLC Media Player"
- (Uses `winget` behind the scenes; requires confirmation in Safe Mode)

## Important Tips

1. **Be specific with app names** - "Open WhatsApp" works better than "Open that app".
2. **Cross-Platform Install** - When you say "Install XYZ", Max will use **Winget** on Windows, **Homebrew** on macOS, and **APT/DNF/Pacman** on Linux.
3. **Paths** - You can use absolute paths or relative paths (like `~/Documents` for your home folder).
4. **Commands are case-insensitive** - "OPEN WHATSAPP", "open whatsapp", "Open WhatsApp" all work.

## Examples of Multi-Step Commands

- "Open Firefox and go to Google" → Opens browser + navigates to google.com
- "Search for the weather" → Opens browser + searches weather on Google
- "Set brightness to 50 and volume to 60" → Adjusts both settings

## Current Limitations

❌ **Not yet supported:**
- Voice control within apps (e.g., "play song on Amazon Music" - must use app UI)
- Real-time screen interaction (typing in web forms beyond simple text input)
- Complex automation (macro-like sequences with conditions)
- Clicking specific UI elements (must use app's native controls)

✅ **Working:**
- App launching (Windows apps, UWP apps, shortcuts, registry installers)
- System volume & brightness
- Basic file operations
- Web navigation
- Text search
- Simple multi-step commands

---

**Pro Tip:** If Max doesn't understand your first command, say it again clearly or rephrase it. The speech recognition (faster-whisper) improves with clearer audio.
