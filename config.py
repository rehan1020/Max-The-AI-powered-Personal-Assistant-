"""Central configuration for Max AI Desktop Agent."""

import os
import platform
import shutil
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# ── OS Detection ─────────────────────────────────────────────────────────
OS = platform.system()
IS_WINDOWS = OS == "Windows"
IS_MACOS = OS == "Darwin"
IS_LINUX = OS == "Linux"

# ── Paths (cross-platform) ───────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).parent.resolve()
BASE_DIR = PROJECT_ROOT
DATA_DIR = PROJECT_ROOT / "data"
LOGS_DIR = PROJECT_ROOT / "logs"
MODELS_DIR = PROJECT_ROOT / "models"
DB_PATH = DATA_DIR / "max_memory.db"
APP_REGISTRY_PATH = DATA_DIR / "app_registry.yaml"

# Create directories
DATA_DIR.mkdir(exist_ok=True)
LOGS_DIR.mkdir(exist_ok=True)
MODELS_DIR.mkdir(exist_ok=True)

# ── Protected paths (never allow deletion/move) ──────────────────────────
PROTECTED_PATHS = [
    BASE_DIR,
    Path.home(),
]
if IS_WINDOWS:
    PROTECTED_PATHS += [Path("C:/Windows"), Path("C:/Program Files")]
elif IS_MACOS:
    PROTECTED_PATHS += [Path("/System"), Path("/Library"), Path("/Applications")]
elif IS_LINUX:
    PROTECTED_PATHS += [Path("/etc"), Path("/usr"), Path("/boot"), Path("/sys")]

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


# ── Chrome (auto-discovery) ───────────────────────────────────────────────
def _find_chrome() -> str:
    """Auto-discover Chrome/Chromium executable on the system."""
    # 1. Check PATH via shutil.which
    for name in ("chrome", "google-chrome", "google-chrome-stable",
                 "chromium", "chromium-browser"):
        found = shutil.which(name)
        if found:
            return found

    # 2. Platform-specific common locations
    if IS_WINDOWS:
        import winreg
        # Try App Paths registry
        try:
            key = winreg.OpenKey(
                winreg.HKEY_LOCAL_MACHINE,
                r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe",
            )
            path, _ = winreg.QueryValueEx(key, "")
            winreg.CloseKey(key)
            if Path(path).exists():
                return path
        except (OSError, FileNotFoundError):
            pass
        # Common install locations
        for candidate in (
            Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Google/Chrome/Application/chrome.exe",
            Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Google/Chrome/Application/chrome.exe",
            Path(os.environ.get("LocalAppData", "")) / "Google/Chrome/Application/chrome.exe",
        ):
            if candidate.exists():
                return str(candidate)
    elif IS_MACOS:
        mac_path = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
        if mac_path.exists():
            return str(mac_path)
    else:  # Linux
        for candidate in ("/usr/bin/google-chrome", "/usr/bin/chromium-browser",
                          "/usr/bin/chromium", "/snap/bin/chromium"):
            if Path(candidate).exists():
                return candidate

    return "chrome"  # fallback — let the OS try to resolve it


def _default_chrome_user_data() -> str:
    """Return default Chrome debug profile directory for the current OS."""
    if IS_WINDOWS:
        return r"C:\chrome-debug-profile"
    elif IS_MACOS:
        return str(Path.home() / "Library/Application Support/Google/Chrome")
    else:
        return str(Path.home() / ".config/google-chrome")


CHROME_PATH = os.getenv("CHROME_PATH", "") or _find_chrome()
CHROME_DEBUG_PORT = int(os.getenv("CHROME_DEBUG_PORT", "9222"))
CHROME_USER_DATA = os.getenv("CHROME_USER_DATA", "") or _default_chrome_user_data()

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

# ── Feature Flags ──────────────────────────────────────────────────────────
STREAMING_RESPONSES = os.getenv("STREAMING_RESPONSES", "true").lower() == "true"
RESPONSE_CACHE_ENABLED = os.getenv("RESPONSE_CACHE_ENABLED", "true").lower() == "true"
RESPONSE_CACHE_TTL = int(os.getenv("RESPONSE_CACHE_TTL", "3600"))
INTERRUPT_ENABLED = os.getenv("INTERRUPT_ENABLED", "true").lower() == "true"
PREVIEW_PLAN_BEFORE_EXEC = os.getenv("PREVIEW_PLAN_BEFORE_EXEC", "false").lower() == "true"
SYSTEM_TRAY_MODE = os.getenv("SYSTEM_TRAY_MODE", "true").lower() == "true"
PLATFORM_NOTIFICATIONS = os.getenv("PLATFORM_NOTIFICATIONS", "true").lower() == "true"

# ── TTS Provider ───────────────────────────────────────────────────────────
TTS_PROVIDER = os.getenv("TTS_PROVIDER", "pyttsx3")
ELEVENLABS_API_KEY = os.getenv("ELEVENLABS_API_KEY", "")
ELEVENLABS_VOICE_ID = os.getenv("ELEVENLABS_VOICE_ID", "21m00Tcm4TlvDq8ikWAM")

# ── Vector Memory ──────────────────────────────────────────────────────────
VECTOR_MEMORY_ENABLED = os.getenv("VECTOR_MEMORY_ENABLED", "false").lower() == "true"

# ── Safety ─────────────────────────────────────────────────────────────────

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

# ── Safety & Control ──────────────────────────────────────────────────────
# If True, only use rule-based parser, do NOT use LLM for complex tasks
SIMPLE_COMMANDS_ONLY = os.getenv("SIMPLE_COMMANDS_ONLY", "false").lower() == "true"

# If True, require confirmation for ALL dangerous actions
REQUIRE_CONFIRMATION_FOR_DANGEROUS = os.getenv("REQUIRE_CONFIRMATION_FOR_DANGEROUS", "true").lower() == "true"

# If True, reject complex multi-step plans
REJECT_COMPLEX_PLANS = os.getenv("REJECT_COMPLEX_PLANS", "false").lower() == "true"

# Maximum number of actions allowed in a single plan
MAX_ACTIONS_PER_PLAN = int(os.getenv("MAX_ACTIONS_PER_PLAN", "10"))

# Actions that always require confirmation (whitelist enforcement)
DANGEROUS_ACTIONS_WHITELIST = {
    "install_software",
    "file_delete",
    "system_shutdown",
    "system_restart",
}

# ── Allowed Action Types ───────────────────────────────────────────────────
ALL_ACTION_TYPES = SAFE_ACTIONS | DANGEROUS_ACTIONS
