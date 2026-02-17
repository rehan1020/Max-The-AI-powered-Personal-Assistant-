"""Hotword detection for wake word "Max".

Uses a two-tier approach:
  1. openwakeword if a trained model is available
  2. Fallback: quick Whisper transcription on short audio segments
     to check if the wake word was spoken.
"""

import logging
import time
import threading
from typing import Callable, Optional
from pathlib import Path

import numpy as np

import config

logger = logging.getLogger(__name__)


class HotwordDetector:
    """Detects the wake word 'Max' from audio input."""

    def __init__(self):
        self.wake_word = config.WAKE_WORD
        self._oww_model = None
        self._whisper_model = None
        self._mode = "whisper_fallback"  # or "openwakeword"
        self._running = False
        self._on_detected: Optional[Callable] = None

        self._try_load_openwakeword()

    def _try_load_openwakeword(self):
        """Try to load openwakeword with a custom model."""
        model_path = config.MODELS_DIR / "max_wakeword.onnx"
        if not model_path.exists():
            logger.info("No openwakeword model found — using Whisper fallback for hotword detection")
            self._mode = "whisper_fallback"
            return

        try:
            from openwakeword.model import Model
            self._oww_model = Model(
                wakeword_models=[str(model_path)],
                inference_framework="onnx",
            )
            self._mode = "openwakeword"
            logger.info("openwakeword model loaded for hotword detection")
        except Exception as e:
            logger.warning(f"Failed to load openwakeword: {e} — using Whisper fallback")
            self._mode = "whisper_fallback"

    def _get_whisper(self):
        """Lazy-load a tiny Whisper model for keyword spotting."""
        if self._whisper_model is None:
            from faster_whisper import WhisperModel
            device = config.WHISPER_DEVICE
            compute_type = "float16" if device == "cuda" else "int8"
            try:
                self._whisper_model = WhisperModel(
                    "tiny", device=device, compute_type=compute_type,
                )
                logger.info(f"Loaded whisper-tiny for hotword detection on {device}")
            except Exception as e:
                logger.warning(f"Failed to load Whisper on {device}: {e} — falling back to CPU")
                self._whisper_model = WhisperModel(
                    "tiny", device="cpu", compute_type="int8",
                )
                logger.info("Loaded whisper-tiny for hotword detection on CPU (fallback)")
        return self._whisper_model

    def check_audio_oww(self, audio: np.ndarray) -> bool:
        """Check audio chunk with openwakeword."""
        if self._oww_model is None:
            return False
        prediction = self._oww_model.predict(audio)
        for key, score in prediction.items():
            if score > 0.5:
                logger.info(f"openwakeword detected: {key} (score={score:.2f})")
                return True
        return False

    def check_audio_whisper(self, audio: np.ndarray) -> bool:
        """Check audio chunk with Whisper tiny — look for wake word."""
        try:
            model = self._get_whisper()
            audio_float = audio.astype(np.float32) / 32768.0
            segments, _ = model.transcribe(
                audio_float,
                language="en",
                beam_size=1,
                best_of=1,
                vad_filter=False,
            )
            text = ""
            for seg in segments:
                text += seg.text
            text = text.strip().lower()
            if not text:
                return False

            # Check if wake word is present
            wake_words = [self.wake_word, f"hey {self.wake_word}", f"hi {self.wake_word}"]
            for ww in wake_words:
                if ww in text:
                    logger.info(f"Hotword detected via Whisper: '{text}'")
                    return True
            return False
        except Exception as e:
            logger.error(f"Whisper hotword check failed: {e}")
            return False

    def check_audio(self, audio: np.ndarray) -> bool:
        """Check if audio contains the wake word."""
        if self._mode == "openwakeword":
            return self.check_audio_oww(audio)
        return self.check_audio_whisper(audio)

    def extract_command(self, text: str) -> Optional[str]:
        """Extract the command portion after the wake word.
        
        e.g. 'Max open Chrome' → 'open Chrome'
        """
        text_lower = text.lower()
        prefixes = [
            f"hey {self.wake_word} ",
            f"hi {self.wake_word} ",
            f"{self.wake_word} ",
            f"hey {self.wake_word}, ",
            f"hi {self.wake_word}, ",
            f"{self.wake_word}, ",
        ]
        for prefix in prefixes:
            idx = text_lower.find(prefix)
            if idx != -1:
                return text[idx + len(prefix):].strip()
        return text.strip()
