"""TTS base class."""

from abc import ABC, abstractmethod


class TTSBase(ABC):
    """Abstract base class for TTS providers."""

    @abstractmethod
    def speak(self, text: str) -> None:
        """Speak the given text.
        
        Args:
            text: The text to speak.
        """
        raise NotImplementedError

    def __call__(self, text: str) -> None:
        """Allow TTS to be called as a function."""
        self.speak(text)
