# 🧠 MAX — AI Voice-Controlled Windows Desktop Agent

Max is a controlled AI-powered Windows orchestration engine with a voice interface. It listens for the wake word **"Max"**, converts voice commands into structured action plans via OpenRouter, validates them for safety, and executes them on your real desktop — browser, files, apps, and system controls.

---

## Features

- **Wake word activation** — say "Max" to trigger
- **Speech-to-text** — local transcription via faster-whisper (GPU-accelerated)
- **AI task planning** — natural language → structured JSON plans via OpenRouter
- **Browser automation** — controls your real Chrome (visible, with your cookies/sessions)
- **Mouse & keyboard** — full desktop control via PyAutoGUI
- **File management** — create, move, delete files (with protection)
- **System control** — volume, brightness, app launching, software installation
- **Screen reading** — screenshots + OCR via EasyOCR
- **Safety layer** — dangerous actions require manual confirmation
- **Persistent memory** — SQLite database stores conversations across sessions
- **Professional GUI** — dark-themed PyQt6 interface with conversation log, action log, and status bar
- **Windows auto-startup** — optional boot-on-login via startup shortcut or registry

---

## Requirements

- **Windows 10/11**
- **Python 3.14** (or 3.13+)
- **NVIDIA GPU** recommended (RTX 2050 or better) for fast Whisper transcription
- **Google Chrome** installed
- **Microphone** for voice input
- **Speakers** for TTS responses
- **OpenRouter API key** (free tier works)

---

## Installation

### 1. Clone or download the project

Place the `voice` folder wherever you like (e.g. `C:\Users\YourName\Downloads\voice`).

### 2. Create the virtual environment

```powershell
cd C:\Users\30reh\Downloads\voice
py -3.14 -m venv venv
```

### 3. Activate the virtual environment

```powershell
.\venv\Scripts\Activate.ps1
```

### 4. Install dependencies

```powershell
pip install -r requirements.txt
```

If `webrtcvad` fails (requires C++ Build Tools), skip it — the system automatically falls back to energy-based voice activity detection:

```powershell
pip install python-dotenv httpx openai PyQt6 pyttsx3 pyautogui pyperclip mss psutil screen-brightness-control numpy sounddevice pycaw faster-whisper playwright easyocr Pillow
```

### 5. Install Playwright browser binaries

```powershell
playwright install chromium
```

### 6. Configure environment variables

Edit the `.env` file in the project root:

```env
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_MODEL=google/gemini-2.0-flash-exp:free
CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe
CHROME_DEBUG_PORT=9222
CHROME_USER_DATA=C:\chrome-debug-profile
WHISPER_MODEL=small
WHISPER_DEVICE=cuda
TTS_VOICE_GENDER=male
WAKE_WORD=max
LOG_LEVEL=INFO
```

| Variable | Description |
|---|---|
| `OPENROUTER_API_KEY` | Your OpenRouter API key ([get one free](https://openrouter.ai/keys)) |
| `OPENROUTER_MODEL` | AI model to use (free tier: `google/gemini-2.0-flash-exp:free`) |
| `CHROME_PATH` | Path to your Chrome executable |
| `CHROME_DEBUG_PORT` | Port for Chrome remote debugging (default: 9222) |
| `CHROME_USER_DATA` | Folder for Chrome debug profile (keeps sessions separate) |
| `WHISPER_MODEL` | Whisper model size: `tiny`, `base`, `small`, `medium`, `large-v3` |
| `WHISPER_DEVICE` | `cuda` for GPU, `cpu` for CPU-only |
| `TTS_VOICE_GENDER` | `male` or `female` for text-to-speech voice |
| `WAKE_WORD` | Wake word to activate Max (default: `max`) |
| `LOG_LEVEL` | Logging level: `DEBUG`, `INFO`, `WARNING`, `ERROR` |

---

## Usage

### Launch Max

```powershell
cd C:\Users\30reh\Downloads\voice
.\venv\Scripts\python.exe main.py
```

### GUI Controls

| Control | Action |
|---|---|
| **▶ Start Listening** | Begin wake word detection |
| **■ Stop** | Stop listening |
| **Safe Mode** checkbox | When ON, all dangerous actions show a confirmation dialog |
| **Left panel** | Conversation history |
| **Right panel** | Action execution log with JSON plans |
| **Bottom bar** | Listening status, internet indicator, memory count |

### Voice Commands — Examples

| Say this | What Max does |
|---|---|
| "Max, open Chrome" | Launches Chrome with remote debugging |
| "Max, go to YouTube" | Navigates to youtube.com |
| "Max, search for Python tutorials" | Opens Google search |
| "Max, open Notepad" | Launches Notepad |
| "Max, set volume to 50" | Sets system volume to 50% |
| "Max, set brightness to 80" | Sets screen brightness to 80% |
| "Max, create a file called notes.txt on my desktop" | Creates the file |
| "Max, delete the file test.txt on my desktop" | Deletes (with confirmation) |
| "Max, install VS Code" | Installs via winget (with confirmation) |
| "Max, close Chrome" | Terminates Chrome |
| "Max, read the screen" | OCR captures visible text |
| "Max, what's on my screen" | Takes screenshot for summarization |

---

## Architecture

```
[Hotword Engine]  ←  openwakeword or Whisper-tiny fallback
        ↓
[Speech-to-Text]  ←  faster-whisper (GPU)
        ↓
[Intent Router]
        ↓
[AI Task Planner]  ←  OpenRouter API (free tier)
        ↓
[Structured JSON Plan]
        ↓
[Safety Validator]  ←  classifies safe / dangerous / blocked
        ↓
[Confirmation Dialog]  ←  PyQt6 popup (if dangerous)
        ↓
[Execution Engine]  ←  dispatches to handlers
        ↓
[System / Browser Control]
        ↓
[Voice Response]  ←  pyttsx3 TTS
        ↓
[Memory Storage]  ←  SQLite database
```

### Project Structure

```
voice/
├── .env                          # API keys & config
├── .gitignore
├── requirements.txt
├── config.py                     # Central configuration
├── main.py                       # Entry point
├── core/
│   ├── orchestrator.py           # Main pipeline coordinator
│   ├── voice/
│   │   ├── audio_capture.py      # Mic input + VAD
│   │   ├── hotword.py            # Wake word detection
│   │   ├── stt.py                # Speech-to-text (Whisper)
│   │   └── tts.py                # Text-to-speech (pyttsx3)
│   ├── ai/
│   │   ├── prompt.py             # System prompt + context builder
│   │   ├── schema.py             # JSON plan validation
│   │   └── openrouter.py         # OpenRouter API client
│   ├── safety/
│   │   └── validator.py          # Action classification + protection
│   ├── execution/
│   │   ├── browser_control.py    # Playwright + Chrome CDP
│   │   ├── mouse_keyboard.py     # PyAutoGUI desktop control
│   │   ├── file_manager.py       # Safe file operations
│   │   ├── system_control.py     # Volume, brightness, apps, installs
│   │   ├── screen_reader.py      # Screenshots + EasyOCR
│   │   └── dispatcher.py         # Action → handler mapping
│   └── memory/
│       └── database.py           # SQLite conversations + preferences
├── gui/
│   ├── styles.py                 # Dark theme stylesheet
│   ├── widgets.py                # Custom UI panels
│   └── main_window.py            # PyQt6 main window
├── startup/
│   └── install_startup.py        # Windows auto-start installer
├── data/                         # SQLite database (auto-created)
├── logs/                         # Log files (auto-created)
└── models/                       # Wake word models (optional)
```

---

## Action Types

Max understands the following action types. The AI planner converts natural language to these structured actions:

### Safe Actions (no confirmation needed)

| Action | Parameters | Description |
|---|---|---|
| `open_app` | `name` | Open an application |
| `close_app` | `name` | Close an application |
| `open_browser` | `browser` | Launch Chrome |
| `navigate` | `url` | Go to a URL |
| `click` | `x, y` / `selector` / `text` | Click element or coordinates |
| `type_text` | `text` | Type text |
| `move_mouse` | `x, y` | Move cursor |
| `file_create` | `path, content` | Create a file |
| `summarize_screen` | — | Capture screenshot |
| `read_screen` | `region` | OCR the screen |
| `search_web` | `query` | Google search |
| `wait` | `seconds, message` | Pause execution |

### Dangerous Actions (confirmation required in Safe Mode)

| Action | Parameters | Description |
|---|---|---|
| `file_delete` | `path` | Delete a file or folder |
| `file_move` | `source, destination` | Move/rename a file |
| `install_software` | `name, method, package_id` | Install via winget/choco |
| `system_volume` | `level` / `action` | Change volume or mute |
| `system_brightness` | `level` | Change brightness |
| `press_key` | `key` | Press key combo (can be destructive) |

---

## Safety & Security

- **No `eval()`** — AI output is never executed as code
- **No direct shell from LLM** — the AI is a planner, not an executor
- **JSON validation** — every AI response is parsed and validated against a strict schema
- **Protected paths** — Max cannot modify its own project directory, `C:\Windows`, or Program Files
- **URL validation** — blocks `javascript:`, `data:`, and `file:///` URLs
- **Key combo safety** — dangerous combos like `Alt+F4`, `Ctrl+Alt+Delete` require confirmation
- **Action logging** — every action is logged to file and displayed in the GUI
- **Safe Mode toggle** — enable/disable confirmation dialogs from the GUI

---

## Memory System

Max stores all interactions in a SQLite database (`data/max_memory.db`):

- **Conversations table** — timestamp, user text, AI plan, execution result, success flag
- **Preferences table** — key-value store for user settings
- **Context injection** — last 5 conversations are included in AI prompts for continuity
- **Auto-cleanup** — old conversations can be pruned (keeps latest 1000 by default)

---

## Windows Auto-Startup

To make Max start when you log in:

```python
from startup.install_startup import install_startup, remove_startup, is_startup_enabled

install_startup()      # Add to startup
remove_startup()       # Remove from startup
is_startup_enabled()   # Check status
```

Or build a standalone executable first:

```powershell
pip install pyinstaller
pyinstaller --onefile --windowed --name "Max AI Agent" main.py
```

Then place the `.exe` shortcut in `shell:startup`.

---

## Troubleshooting

| Issue | Solution |
|---|---|
| **"OPENROUTER_API_KEY not set"** | Edit `.env` and add your key from [openrouter.ai/keys](https://openrouter.ai/keys) |
| **No sound from TTS** | Check Windows sound settings, ensure speakers are connected |
| **Whisper loads slowly** | First run downloads the model (~500MB for `small`). Use `tiny` for faster startup |
| **"Chrome not found"** | Update `CHROME_PATH` in `.env` to your actual Chrome location |
| **GPU not detected** | Set `WHISPER_DEVICE=cpu` in `.env`. CUDA requires NVIDIA GPU + drivers |
| **webrtcvad install fails** | Skip it — energy-based VAD is used as fallback automatically |
| **Rate limited by OpenRouter** | Free tier has limits. Wait a moment or upgrade your plan |
| **PyQt6 window is blank** | Update your GPU drivers. PyQt6 requires OpenGL support |
| **Microphone not working** | Check Windows privacy settings → Microphone access for desktop apps |

---

## Configuration Tips

### Use a faster/smaller Whisper model

For faster response on weaker hardware:
```env
WHISPER_MODEL=tiny
WHISPER_DEVICE=cpu
```

### Use a different AI model

Any OpenRouter-compatible model works:
```env
OPENROUTER_MODEL=meta-llama/llama-3-8b-instruct:free
```

### Change the wake word

```env
WAKE_WORD=jarvis
```

### Increase recording time

Edit `config.py`:
```python
RECORDING_MAX_SECONDS = 60  # default is 30
```

---

## License

Personal use project. Not affiliated with OpenRouter, Google, or Microsoft.
