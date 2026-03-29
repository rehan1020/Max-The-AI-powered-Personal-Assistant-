"""Text-to-Speech using ElevenLabs API (premium cloud TTS)."""

import io
import threading

import httpx
import numpy as np
import sounddevice as sd

from core.logger import logger
from core.voice.tts_base import TTSBase


class ElevenLabsTTS(TTSBase):
    """Speaks text aloud using ElevenLabs API."""

    def __init__(self, api_key: str, voice_id: str = "21m00Tcm4TlvDq8ikWAM"):
        """Initialize ElevenLabs TTS.
        
        Args:
            api_key: ElevenLabs API key.
            voice_id: The voice ID to use.
        """
        self.api_key = api_key
        self.voice_id = voice_id
        self.base_url = "https://api.elevenlabs.io/v1"

    def speak(self, text: str):
        """Speak text aloud using ElevenLabs."""
        if not text or not self.api_key:
            return

        try:
            logger.info(f"ElevenLabs TTS: {text[:100]}...")

            response = httpx.post(
                f"{self.base_url}/text-to-speech/{self.voice_id}",
                headers={
                    "Accept": "audio/mpeg",
                    "Content-Type": "application/json",
                    "xi-api-key": self.api_key,
                },
                json={
                    "text": text,
                    "model_id": "eleven_monolingual_v1",
                    "voice_settings": {
                        "stability": 0.5,
                        "similarity_boost": 0.5,
                    },
                },
                timeout=30.0,
            )

            if response.status_code != 200:
                logger.error(f"ElevenLabs error: {response.status_code} {response.text}")
                return

            audio_data = io.BytesIO(response.content)
            audio_array = np.frombuffer(audio_data.read(), dtype=np.int16)

            sd.play(audio_array.astype(np.float32) / 32768.0, 24000)
            sd.wait()

        except Exception as e:
            logger.error(f"ElevenLabs TTS failed: {e}")

    def speak_async(self, text: str):
        """Speak text in a background thread."""
        thread = threading.Thread(target=self.speak, args=(text,), daemon=True)
        thread.start()

    def stop(self):
        """Stop any current speech."""
        try:
            sd.stop()
        except Exception:
            pass
