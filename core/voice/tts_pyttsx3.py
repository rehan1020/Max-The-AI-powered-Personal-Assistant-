"""Text-to-Speech using pyttsx3 (offline, cross-platform)."""

import threading
from typing import Optional

import pyttsx3

import config
from core.logger import logger
from core.voice.tts_base import TTSBase


class Pyttsx3TTS(TTSBase):
    """Speaks text aloud using pyttsx3."""

    def __init__(self):
        self._engine = None
        self._lock = threading.Lock()
        self._init_engine()

    def _init_engine(self):
        """Initialize the TTS engine."""
        try:
            self._engine = pyttsx3.init()
            self._engine.setProperty("rate", 175)
            self._engine.setProperty("volume", 0.9)

            voices = self._engine.getProperty("voices")
            target_gender = config.TTS_VOICE_GENDER.lower()

            selected = None
            for voice in voices:
                name_lower = voice.name.lower()
                if target_gender == "male" and ("david" in name_lower or "mark" in name_lower or "male" in name_lower):
                    selected = voice
                    break
                elif target_gender == "female" and ("zira" in name_lower or "hazel" in name_lower or "female" in name_lower):
                    selected = voice
                    break

            if selected:
                self._engine.setProperty("voice", selected.id)
                logger.info(f"TTS voice: {selected.name}")
            elif voices:
                self._engine.setProperty("voice", voices[0].id)
                logger.info(f"TTS voice (default): {voices[0].name}")

            logger.info("pyttsx3 TTS engine initialized")
        except Exception as e:
            logger.error(f"Failed to initialize pyttsx3: {e}")
            self._engine = None

    def speak(self, text: str):
        """Speak text aloud. Thread-safe."""
        if not self._engine or not text:
            return

        with self._lock:
            try:
                logger.info(f"TTS: {text}")
                self._engine.say(text)
                self._engine.runAndWait()
            except Exception as e:
                logger.error(f"TTS failed: {e}")
                self._init_engine()

    def speak_async(self, text: str):
        """Speak text in a background thread."""
        thread = threading.Thread(target=self.speak, args=(text,), daemon=True)
        thread.start()

    def stop(self):
        """Stop any current speech."""
        if self._engine:
            try:
                self._engine.stop()
            except Exception:
                pass
