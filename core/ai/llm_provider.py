"""Abstract LLM provider interface for Max AI planner.

Defines the contract that all LLM providers (cloud and local) must implement.
This enables seamless switching between OpenRouter, Ollama, or any future backend.
"""

from abc import ABC, abstractmethod
from typing import AsyncGenerator, Optional


class LLMProvider(ABC):
    """Base class for all LLM providers."""

    @abstractmethod
    def plan(
        self,
        user_text: str,
        recent_conversations: list[dict] = None,
    ) -> Optional[dict]:
        """Convert user text to a validated action plan.

        Args:
            user_text: The user's voice command (transcribed).
            recent_conversations: Recent history for context.

        Returns:
            Validated action plan dict, or None on failure.
        """
        raise NotImplementedError

    async def stream_plan(
        self,
        user_text: str,
        recent_conversations: list[dict] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream the LLM response as an async generator.
        
        Override this method in subclasses to enable streaming.
        
        Args:
            user_text: The user's voice command (transcribed).
            recent_conversations: Recent history for context.
            
        Yields:
            Tokens as they arrive from the LLM.
        """
        yield ""

    @abstractmethod
    def close(self):
        """Release any resources held by the provider."""
        raise NotImplementedError

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Human-readable name of this provider (for logging)."""
        raise NotImplementedError
