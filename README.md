# 🧠 MAX — AI Voice-Controlled Windows Desktop Agent

Max is a full-featured AI-powered Windows orchestration engine with a voice interface. It listens for the wake word **"Max"**, converts voice commands into structured action plans using your choice of **local Ollama or cloud OpenRouter LLMs**, validates them for safety, and executes them on your real desktop — browser automation, file management, system control, and more.

---
## UPDATE

v2 brings a lot of new things soon.
---

## Features

- **Wake word activation** — say "Max" to trigger
- **Speech-to-text** — local transcription via faster-whisper (GPU-accelerated)
- **Flexible LLM support** — run locally with Ollama (open-source) or use OpenRouter cloud (multiple models). Includes automatic fallback: if primary fails, switches to secondary provider seamlessly
- **AI task planning** — natural language → structured JSON plans
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
- **LLM configuration** (choose one or both):
  - **OpenRouter API key** ([free tier works](https://openrouter.ai/keys)) for cloud-based LLMs
  - **Ollama** ([ollama.ai](https://ollama.ai)) for local, privacy-first LLM execution

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
# LLM Provider Configuration
LLM_PROVIDER=auto
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OPENROUTER_MODEL=google/gemini-2.0-flash-exp:free
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=phi3:mini

# Browser & Chrome
CHROME_PATH=C:\Program Files\Google\Chrome\Application\chrome.exe
CHROME_DEBUG_PORT=9222
CHROME_USER_DATA=C:\chrome-debug-profile

# Speech & Audio
WHISPER_MODEL=small
WHISPER_DEVICE=cuda
TTS_VOICE_GENDER=male
WAKE_WORD=max

# Logging
LOG_LEVEL=INFO
```

| Variable | Description |
|---|---|
| `LLM_PROVIDER` | `"local"` (Ollama only), `"cloud"` (OpenRouter only), or `"auto"` (try Ollama first, fall back to OpenRouter) |
| `OPENROUTER_API_KEY` | Your OpenRouter API key ([get one free](https://openrouter.ai/keys)) — required if using OpenRouter |
| `OPENROUTER_MODEL` | AI model to use (free tier: `google/gemini-2.0-flash-exp:free`) |
| `OLLAMA_BASE_URL` | Ollama server URL (default: `http://localhost:11434`) |
| `OLLAMA_MODEL` | Local model to use (default: `phi3:mini`) |
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
| "Max, open Chrome" | Launches Chrome (safe) |
| "Max, go to YouTube" | Navigates to youtube.com (safe) |
| "Max, search for Python tutorials" | Opens Google search (safe) |
| "Max, open Notepad" | Launches Notepad (safe) |
| "Max, click Play" | Clicks element with "Play" text (safe) |
| "Max, type hello world" | Types text (safe) |
| "Max, set volume to 50" | Sets system volume (dangerous, needs confirmation) |
| "Max, set brightness to 80" | Sets screen brightness (dangerous, needs confirmation) |
| "Max, create a file called notes.txt" | Creates a text file (safe) |
| "Max, delete the file test.txt" | Deletes file (dangerous, needs confirmation) |
| "Max, install VS Code" | Installs via winget (dangerous, needs confirmation) |
| "Max, close Chrome" | Terminates Chrome (safe) |
| "Max, read the screen" | Captures + OCRs visible text (safe) |
| "Max, what's on my screen" | Takes screenshot for summarization (safe) |
| "Max, lock the screen" | Locks Windows (system control) |
| "Max, sleep" | Puts system to sleep (system control) |
| "Max, turn WiFi off" | Toggles WiFi (system control) |
| "Max, mute" | Mutes audio (system control) |

---

## Architecture

```
User Command
    ↓
[1] Rule-Based Parser (fast, deterministic, safe)
    ↓
  Rule match? → Direct execution
  ↓
  No rule? → Check if simple-only mode
    ↓
  NO → Continue to LLM
    ↓
[2] LLM Task Planner  ←  Multi-provider LLM
                         ├─ Ollama (local)
                         └─ OpenRouter (cloud)
    ↓
[3] JSON Plan Validator
    ↓
[4] Safety Classifier (allowed/dangerous/blocked)
    ↓
[5] User Confirmation (if needed)
    ↓
[6] Action Dispatcher
    ↓
[7] Execution Handlers
    ↓
[8] Voice Response + Memory
```

### Key Improvements

- **Rule-Based Parser** (`core/ai/rule_parser.py`) — Fast, deterministic handling of common commands without LLM overhead
- **Plan Validator** (`core/ai/plan_validator.py`) — Validates action schemas and detects complexity
- **Safety Architecture** — See [SAFETY_ARCHITECTURE.md](SAFETY_ARCHITECTURE.md) for detailed safety layers
- **Multi-Provider LLM** — Automatic fallback between Ollama (local) and OpenRouter (cloud)
- **Action Dispatcher** — Thread-safe execution with async support for browser operations

### Project Structure

```
voice/
├── .env                          # Configuration (copy from .env.example)
├── .env.example                  # Example configuration template
├── .gitignore
├── requirements.txt
├── README.md                     # This file
├── COMMANDS.md                   # Voice command examples
├── IMPROVEMENTS.md               # Recent improvements & features
├── SAFETY_ARCHITECTURE.md        # Safety layer documentation
├── config.py                     # Central configuration
├── main.py                       # Entry point
├── core/
│   ├── orchestrator.py           # Main pipeline coordinator
│   ├── voice/
│   │   ├── audio_capture.py      # Mic input + VAD (webrtcvad or energy-based)
│   │   ├── hotword.py            # Wake word detection (openwakeword)
│   │   ├── stt.py                # Speech-to-text (faster-whisper, GPU-accelerated)
│   │   └── tts.py                # Text-to-speech (pyttsx3)
│   ├── ai/
│   │   ├── provider_factory.py   # Multi-provider LLM system with fallback
│   │   ├── llm_provider.py       # Base LLM interface
│   │   ├── openrouter.py         # OpenRouter API client (cloud)
│   │   ├── ollama_provider.py    # Ollama client (local)
│   │   ├── rule_parser.py        # Rule-based command parser (fast path)
│   │   ├── plan_validator.py     # JSON plan validation + complexity checking
│   │   ├── prompt.py             # System prompt + context builder
│   │   └── schema.py             # Original JSON schema validator
│   ├── safety/
│   │   └── validator.py          # Action classification + protection
│   ├── execution/
│   │   ├── dispatcher.py         # Action execution engine
│   │   ├── browser_control.py    # Playwright + Chrome CDP automation
│   │   ├── mouse_keyboard.py     # PyAutoGUI desktop control
│   │   ├── file_manager.py       # Safe file operations (protected paths)
│   │   ├── system_control.py     # Volume, brightness, apps, installs, WiFi, etc.
│   │   └── screen_reader.py      # Screenshots + EasyOCR text extraction
│   └── memory/
│       └── database.py           # SQLite conversations + user preferences
├── gui/
│   ├── main_window.py            # PyQt6 main application window
│   ├── widgets.py                # Custom UI components
│   └── styles.py                 # Dark theme stylesheet
├── startup/
│   └── install_startup.py        # Windows auto-start installer
├── test_llm_commands.py          # Test LLM provider integration
├── test_subsystems.py            # Test individual subsystems
├── test_safety_features.py       # Test safety validators
├── data/                         # SQLite database directory (auto-created)
├── logs/                         # Log files directory (auto-created)
└── models/                       # Voice/hotword models (optional)
```

---

## Action Types

Max understands the following action types. The AI planner converts natural language to these structured actions:

### Safe Actions (no confirmation needed)

| Action | Parameters | Description |
|---|---|---|
| `open_app` | `name` | Open an application (e.g., "Notepad", "VS Code") |
| `close_app` | `name` | Close an application |
| `open_browser` | `browser` | Launch Chrome (or other configured browser) |
| `navigate` | `url` | Navigate to a URL |
| `search_web` | `query` | Perform a Google search |
| `click` | `x, y` or `text` or `selector` | Click element by coordinates, visible text, or CSS selector |
| `type_text` | `text` | Type text into focused element |
| `move_mouse` | `x, y` | Move cursor to coordinates |
| `file_create` | `path, content` | Create a file with optional content |
| `read_screen` | `region` (optional) | OCR the screen or region |
| `summarize_screen` | — | Take screenshot and describe contents |
| `wait` | `seconds, message` | Pause execution (for timing-dependent actions) |

### Dangerous Actions (confirmation required in Safe Mode)

| Action | Parameters | Description |
|---|---|---|
| `file_delete` | `path` | Delete a file or folder |
| `file_move` | `source, destination` | Move/rename a file or folder |
| `install_software` | `name, method, package_id` | Install via winget or chocolatey |
| `system_volume` | `level` (0-100) | Set volume level |
| `system_brightness` | `level` (0-100) | Set screen brightness |
| `press_key` | `key` | Press key combination (can be destructive) |

### System Control Actions (toggles & switches)

| Action | Parameters | Description |
|---|---|---|
| `system_sleep` | — | Put system to sleep |
| `system_lock` | — | Lock Windows screen |
| `system_shutdown` | `seconds` (optional) | Shutdown PC (default: 60 seconds) |
| `system_restart` | `seconds` (optional) | Restart PC (default: 60 seconds) |
| `system_wifi` | `action` ("on", "off", "toggle") | Control WiFi |
| `system_bluetooth` | `action` ("on", "off", "toggle") | Control Bluetooth |
| `system_screensaver` | `action` ("start", "stop") | Control screensaver |
| `system_mute` | — | Mute audio |
| `system_unmute` | — | Unmute audio |

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

### Use Ollama for local, private LLM execution

Ollama lets you run models locally without internet or API keys:

1. **Install Ollama** from [ollama.ai](https://ollama.ai)
2. **Start Ollama server**:
   ```bash
   ollama serve
   ```
3. **Pull a model** (in another terminal):
   ```bash
   ollama pull phi3:mini    # lightweight, fast
   ollama pull llama2       # more capable but slower
   ollama pull mistral      # good balance of speed/quality
   ```
4. **Configure .env**:
   ```env
   LLM_PROVIDER=local
   OLLAMA_BASE_URL=http://localhost:11434
   OLLAMA_MODEL=phi3:mini
   ```

### Use OpenRouter for cloud-based LLMs

For better quality, use cloud models:

1. **Get API key** from [openrouter.ai/keys](https://openrouter.ai/keys) (free tier available)
2. **Configure .env**:
   ```env
   LLM_PROVIDER=cloud
   OPENROUTER_API_KEY=sk-or-v1-your-key-here
   OPENROUTER_MODEL=google/gemini-2.0-flash-exp:free
   ```

### Automatic fallback between providers

For best reliability, use `auto` mode — tries Ollama first, falls back to OpenRouter if unavailable:

```env
LLM_PROVIDER=auto
OPENROUTER_API_KEY=sk-or-v1-your-key-here
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=phi3:mini
```

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
Under Devlopment, updates will be made, Open for suggestions.
