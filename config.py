"""Central configuration for Max AI Desktop Agent."""

import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── Paths ──────────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.resolve()
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"
MODELS_DIR = PROJECT_ROOT / "models"
DB_PATH = DATA_DIR / "max_memory.db"

# Create directories
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

# ── LLM Provider ───────────────────────────────────────────────────────────
# "local" = Ollama only  |  "cloud" = OpenRouter only  |  "auto" = try local, fallback to cloud
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "local")

# ── Ollama (local) ─────────────────────────────────────────────────────────
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "phi3:mini")
OLLAMA_NUM_CTX = int(os.getenv("OLLAMA_NUM_CTX", "2048"))

# ── OpenRouter (cloud) ────────────────────────────────────────────────────
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY", "")
OPENROUTER_MODEL = os.getenv("OPENROUTER_MODEL", "mistralai/mistral-small-3.1-24b-instruct:free")
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# ── Chrome ─────────────────────────────────────────────────────────────────
CHROME_PATH = os.getenv("CHROME_PATH", r"C:\Program Files\Google\Chrome\Application\chrome.exe")
CHROME_DEBUG_PORT = int(os.getenv("CHROME_DEBUG_PORT", "9222"))
CHROME_USER_DATA = os.getenv("CHROME_USER_DATA", r"C:\chrome-debug-profile")

# ── Whisper ────────────────────────────────────────────────────────────────
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "small")
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cuda")

# ── TTS ────────────────────────────────────────────────────────────────────
TTS_VOICE_GENDER = os.getenv("TTS_VOICE_GENDER", "male")

# ── Wake Word ──────────────────────────────────────────────────────────────
WAKE_WORD = os.getenv("WAKE_WORD", "max").lower()

# ── Audio ──────────────────────────────────────────────────────────────────
AUDIO_SAMPLE_RATE = 16000
AUDIO_CHANNELS = 1
AUDIO_FRAME_DURATION_MS = 30          # frame length for VAD (10, 20, or 30 ms)
SILENCE_THRESHOLD_SECONDS = 1.5       # silence before stopping recording
RECORDING_MAX_SECONDS = 30            # max single recording length

# ── Safety ─────────────────────────────────────────────────────────────────
PROTECTED_PATHS = [
    PROJECT_ROOT,                                    # Max cannot edit itself
    Path(os.environ.get("WINDIR", r"C:\Windows")),   # System directory
    Path(r"C:\Program Files"),
    Path(r"C:\Program Files (x86)"),
]

DANGEROUS_ACTIONS = {
    "file_delete",
    "file_move",
    "install_software",
    "system_volume",
    "system_brightness",
    "press_key",           # can be destructive (Alt+F4, etc.)
}

SAFE_ACTIONS = {
    "open_app",
    "close_app",
    "open_browser",
    "navigate",
    "click",
    "type_text",
    "move_mouse",
    "file_create",
    "summarize_screen",
    "read_screen",
    "search_web",
    "wait",
}

# ── Logging ────────────────────────────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
LOG_FILE = LOGS_DIR / "max.log"

# ── Allowed Action Types ───────────────────────────────────────────────────
ALL_ACTION_TYPES = SAFE_ACTIONS | DANGEROUS_ACTIONS
