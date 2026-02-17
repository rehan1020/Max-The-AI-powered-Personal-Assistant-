"""Speech-to-Text using faster-whisper.

Uses GPU (CUDA) by default for the RTX 2050.
Model: small (configurable).
"""

import logging
from typing import Optional

import numpy as np

import config

logger = logging.getLogger(__name__)


class SpeechToText:
    """Transcribes audio to text using faster-whisper."""

    def __init__(self):
        self._model = None
        self.model_name = config.WHISPER_MODEL
        self.device = config.WHISPER_DEVICE

    def _ensure_model(self):
        """Lazy-load the Whisper model."""
        if self._model is None:
            from faster_whisper import WhisperModel
            device = self.device
            compute_type = "float16" if device == "cuda" else "int8"
            try:
                logger.info(f"Loading Whisper model '{self.model_name}' on {device} ({compute_type})")
                self._model = WhisperModel(
                    self.model_name, device=device, compute_type=compute_type,
                )
            except Exception as e:
                logger.warning(f"Failed to load Whisper on {device}: {e} — falling back to CPU")
                self.device = "cpu"
                self._model = WhisperModel(
                    self.model_name, device="cpu", compute_type="int8",
                )
            logger.info("Whisper model loaded successfully")

    def transcribe(self, audio: np.ndarray) -> Optional[str]:
        """Transcribe int16 audio array to text.
        
        Args:
            audio: numpy int16 array at 16kHz mono
            
        Returns:
            Transcribed text string, or None if empty.
        """
        self._ensure_model()

        try:
            # Convert int16 → float32 normalized
            audio_float = audio.astype(np.float32) / 32768.0

            segments, info = self._model.transcribe(
                audio_float,
                language="en",
                beam_size=8,  # Increased from 5 for better accuracy
                best_of=5,    # Increased from 3 for better quality
                temperature=0.0,  # Deterministic output
                compression_ratio_threshold=2.4,  # Better quality threshold
                no_speech_threshold=0.6,  # More sensitive to speech
                vad_filter=True,
                vad_parameters=dict(
                    min_silence_duration_ms=300,  # More sensitive (was 500)
                    speech_pad_ms=100,  # Reduced padding (was 300)
                    start_thresh=0.5,  # Lower threshold to catch speech start
                    end_thresh=0.5,    # Lower threshold to catch speech end
                ),
            )

            text_parts = []
            for segment in segments:
                text_parts.append(segment.text.strip())

            full_text = " ".join(text_parts).strip()

            if full_text:
                logger.info(f"Transcribed ({info.duration:.1f}s audio): {full_text}")
                return full_text
            else:
                logger.debug("Transcription returned empty text")
                return None

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return None

    def is_loaded(self) -> bool:
        """Check if model is loaded."""
        return self._model is not None
