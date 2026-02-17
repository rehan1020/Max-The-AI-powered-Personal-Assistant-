"""Audio capture with Voice Activity Detection.

Uses sounddevice for mic input and webrtcvad for speech detection.
Produces audio chunks suitable for hotword detection and full transcription.
"""

import logging
import queue
import struct
import time
import threading
from typing import Callable, Optional

import numpy as np
import sounddevice as sd

import config

logger = logging.getLogger(__name__)


class AudioCapture:
    """Continuously captures audio from the microphone with VAD."""

    def __init__(self):
        self.sample_rate = config.AUDIO_SAMPLE_RATE
        self.channels = config.AUDIO_CHANNELS
        self.frame_duration_ms = config.AUDIO_FRAME_DURATION_MS
        self.frame_size = int(self.sample_rate * self.frame_duration_ms / 1000)
        self.silence_threshold = config.SILENCE_THRESHOLD_SECONDS
        self.max_recording = config.RECORDING_MAX_SECONDS

        self._audio_queue: queue.Queue = queue.Queue()
        self._stream: Optional[sd.InputStream] = None
        self._running = False
        self._vad = None

    def _init_vad(self):
        """Initialize WebRTC VAD."""
        try:
            import webrtcvad
            self._vad = webrtcvad.Vad(2)  # aggressiveness 0-3
            logger.info("WebRTC VAD initialized (aggressiveness=2)")
        except ImportError:
            logger.warning("webrtcvad not installed — VAD disabled, using energy-based detection")
            self._vad = None

    def _audio_callback(self, indata, frames, time_info, status):
        """Called by sounddevice for each audio block."""
        if status:
            logger.warning(f"Audio status: {status}")
        self._audio_queue.put(indata.copy())

    def start_stream(self):
        """Start the audio input stream."""
        self._init_vad()
        self._running = True
        self._stream = sd.InputStream(
            samplerate=self.sample_rate,
            channels=self.channels,
            dtype="int16",
            blocksize=self.frame_size,
            callback=self._audio_callback,
        )
        self._stream.start()
        logger.info(f"Audio stream started (rate={self.sample_rate}, frame={self.frame_size})")

    def stop_stream(self):
        """Stop the audio input stream."""
        self._running = False
        if self._stream:
            self._stream.stop()
            self._stream.close()
            self._stream = None
        logger.info("Audio stream stopped")

    def is_speech(self, audio_frame: np.ndarray) -> bool:
        """Check if an audio frame contains speech."""
        if self._vad is not None:
            try:
                raw = audio_frame.tobytes()
                return self._vad.is_speech(raw, self.sample_rate)
            except Exception:
                pass

        # Fallback: energy-based detection
        energy = np.abs(audio_frame).mean()
        return energy > 500

    def wait_for_speech(self, timeout: float = 0.0) -> bool:
        """Block until speech is detected. Returns True if speech found."""
        start = time.time()
        while self._running:
            if timeout > 0 and (time.time() - start) > timeout:
                return False
            try:
                frame = self._audio_queue.get(timeout=0.5)
                if self.is_speech(frame):
                    # Put it back so record_utterance captures it
                    self._audio_queue.put(frame)
                    return True
            except queue.Empty:
                continue
        return False

    def record_utterance(self) -> Optional[np.ndarray]:
        """Record audio until silence is detected after speech.
        
        Returns the full audio as int16 numpy array, or None if nothing captured.
        """
        frames = []
        silence_frames = 0
        frames_for_silence = int(self.silence_threshold * 1000 / self.frame_duration_ms)
        max_frames = int(self.max_recording * 1000 / self.frame_duration_ms)
        speech_detected = False

        logger.debug("Recording utterance...")

        while self._running and len(frames) < max_frames:
            try:
                frame = self._audio_queue.get(timeout=1.0)
            except queue.Empty:
                if speech_detected:
                    break
                continue

            frames.append(frame)

            if self.is_speech(frame):
                speech_detected = True
                silence_frames = 0
            else:
                if speech_detected:
                    silence_frames += 1
                    if silence_frames >= frames_for_silence:
                        logger.debug(f"Silence detected after {len(frames)} frames")
                        break

        if not frames or not speech_detected:
            return None

        audio = np.concatenate(frames, axis=0).flatten()
        duration = len(audio) / self.sample_rate
        logger.info(f"Recorded {duration:.1f}s of audio")
        return audio

    def get_short_buffer(self, duration_ms: int = 2000) -> Optional[np.ndarray]:
        """Get a short audio buffer for hotword checking."""
        frames_needed = int(duration_ms / self.frame_duration_ms)
        frames = []
        
        for _ in range(frames_needed):
            try:
                frame = self._audio_queue.get(timeout=0.1)
                frames.append(frame)
            except queue.Empty:
                break

        if not frames:
            return None
        return np.concatenate(frames, axis=0).flatten()

    def clear_queue(self):
        """Clear any buffered audio."""
        while not self._audio_queue.empty():
            try:
                self._audio_queue.get_nowait()
            except queue.Empty:
                break
