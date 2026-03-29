"""Startup validation checks for Max AI Agent.

Runs checks before the main window appears to identify missing dependencies.
"""

import platform
import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class CheckResult:
    """Result of a startup check."""
    name: str
    passed: bool
    message: str
    is_critical: bool = True


def run_all_checks() -> list[CheckResult]:
    """Run all startup checks.
    
    Returns:
        List of CheckResult objects.
    """
    results = []

    results.append(_check_python_version())
    results.append(_check_env_file())
    results.append(_check_llm_connectivity())
    results.append(_check_microphone())
    results.append(_check_platform_adapter())
    results.append(_check_required_directories())

    return results


def _check_python_version() -> CheckResult:
    """Check Python version is 3.11+."""
    ok = sys.version_info >= (3, 11)
    return CheckResult(
        "Python version",
        ok,
        f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}" if ok else "Python 3.11+ required",
        is_critical=True
    )


def _check_env_file() -> CheckResult:
    """Check .env file exists."""
    env_path = Path(".env")
    env_example = Path(".env.example")
    
    if env_path.exists():
        return CheckResult(".env file", True, "Found .env", is_critical=True)
    
    if env_example.exists():
        return CheckResult(
            ".env file",
            False,
            ".env missing — copy .env.example to .env",
            is_critical=True
        )
    
    return CheckResult(
        ".env file",
        False,
        ".env.example not found",
        is_critical=True
    )


def _check_llm_connectivity() -> CheckResult:
    """Check LLM provider is available."""
    try:
        import config
        
        if config.LLM_PROVIDER == "local":
            try:
                import httpx
                resp = httpx.get(f"{config.OLLAMA_BASE_URL}/api/tags", timeout=5)
                if resp.status_code == 200:
                    return CheckResult("Ollama", True, f"Ollama available at {config.OLLAMA_BASE_URL}", is_critical=False)
            except Exception:
                pass
            return CheckResult(
                "Ollama",
                False,
                "Ollama not available — set LLM_PROVIDER=cloud or install Ollama",
                is_critical=False
            )
        elif config.LLM_PROVIDER == "cloud":
            if config.OPENROUTER_API_KEY:
                return CheckResult("OpenRouter", True, "API key configured", is_critical=False)
            return CheckResult(
                "OpenRouter",
                False,
                "OPENROUTER_API_KEY not set",
                is_critical=False
            )
        else:
            return CheckResult("LLM provider", True, f"Using {config.LLM_PROVIDER}", is_critical=False)
    except Exception as e:
        return CheckResult("LLM provider", False, str(e), is_critical=False)


def _check_microphone() -> CheckResult:
    """Check microphone is available."""
    try:
        import sounddevice as sd
        devices = sd.query_devices()
        if devices:
            return CheckResult("Microphone", True, "Microphone available", is_critical=True)
    except Exception as e:
        pass
    
    try:
        import pyaudio
        p = pyaudio.PyAudio()
        device_count = p.get_device_count()
        p.terminate()
        if device_count > 0:
            return CheckResult("Microphone", True, f"{device_count} audio device(s) found", is_critical=True)
    except Exception:
        pass
    
    return CheckResult(
        "Microphone",
        False,
        "No microphone detected — voice commands will not work",
        is_critical=True
    )


def _check_platform_adapter() -> CheckResult:
    """Check platform adapter can initialize."""
    try:
        from core.platform import get_adapter
        adapter = get_adapter()
        os_name = adapter.get_os_name()
        return CheckResult("Platform", True, f"Running on {os_name}", is_critical=False)
    except Exception as e:
        return CheckResult(
            "Platform",
            False,
            f"Failed to initialize platform adapter: {e}",
            is_critical=True
        )


def _check_required_directories() -> CheckResult:
    """Check required directories exist or can be created."""
    try:
        import config
        dirs = [config.DATA_DIR, config.LOGS_DIR, config.MODELS_DIR]
        for d in dirs:
            d.mkdir(parents=True, exist_ok=True)
        return CheckResult("Directories", True, "All required directories available", is_critical=False)
    except Exception as e:
        return CheckResult(
            "Directories",
            False,
            f"Failed to create directories: {e}",
            is_critical=True
        )


def check_chrome() -> CheckResult:
    """Check Chrome/Chromium is available."""
    import config
    
    try:
        result = subprocess.run(
            [config.CHROME_PATH, "--version"],
            capture_output=True,
            timeout=5
        )
        if result.returncode == 0:
            return CheckResult("Chrome", True, result.stdout.decode().strip(), is_critical=False)
    except FileNotFoundError:
        pass
    except Exception:
        pass
    
    return CheckResult(
        "Chrome",
        False,
        "Chrome not found — browser automation may not work",
        is_critical=False
    )


def get_summary(results: list[CheckResult]) -> tuple[int, int]:
    """Get summary counts.
    
    Returns:
        Tuple of (passed_count, failed_count)
    """
    passed = sum(1 for r in results if r.passed)
    failed = sum(1 for r in results if not r.passed)
    return passed, failed


def has_critical_failures(results: list[CheckResult]) -> bool:
    """Check if any critical checks failed."""
    return any(not r.passed and r.is_critical for r in results)
