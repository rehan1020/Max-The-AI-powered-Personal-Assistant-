"""TTS factory - creates the appropriate TTS provider based on config."""

import config
from core.voice.tts_base import TTSBase


def get_tts() -> TTSBase:
    """Get the configured TTS provider.
    
    Returns:
        The TTS provider instance.
    """
    if config.TTS_PROVIDER == "elevenlabs" and config.ELEVENLABS_API_KEY:
        from core.voice.tts_elevenlabs import ElevenLabsTTS
        return ElevenLabsTTS(config.ELEVENLABS_API_KEY, config.ELEVENLABS_VOICE_ID)
    else:
        from core.voice.tts_pyttsx3 import Pyttsx3TTS
        return Pyttsx3TTS()
