"""LLM provider factory with automatic fallback.

Selects the right LLM backend based on config.LLM_PROVIDER:
  - "local"  → OllamaProvider (phi3:mini by default)
  - "cloud"  → OpenRouterClient
  - "auto"   → Try local first; fall back to cloud if unavailable

Also provides a FallbackProvider that wraps both and retries on the
secondary provider when the primary one fails.
"""

import logging
from typing import Optional

import config
from core.ai.llm_provider import LLMProvider

logger = logging.getLogger(__name__)


class FallbackProvider(LLMProvider):
    """Wraps a primary and secondary provider.

    Tries the primary; if it returns None twice, retries on the secondary.
    """

    def __init__(self, primary: LLMProvider, secondary: LLMProvider):
        self._primary = primary
        self._secondary = secondary
        self._consecutive_primary_failures = 0
        self._failure_threshold = 2

    @property
    def provider_name(self) -> str:
        return (
            f"Fallback({self._primary.provider_name} → "
            f"{self._secondary.provider_name})"
        )

    def plan(
        self,
        user_text: str,
        recent_conversations: list[dict] = None,
    ) -> Optional[dict]:
        # Try primary
        result = self._primary.plan(user_text, recent_conversations)
        if result is not None:
            self._consecutive_primary_failures = 0
            return result

        self._consecutive_primary_failures += 1
        logger.warning(
            f"{self._primary.provider_name} failed "
            f"({self._consecutive_primary_failures}/{self._failure_threshold}). "
            f"Falling back to {self._secondary.provider_name}."
        )

        # Try secondary
        result = self._secondary.plan(user_text, recent_conversations)
        if result is not None:
            return result

        logger.error("Both primary and secondary providers failed.")
        return None

    def close(self):
        self._primary.close()
        self._secondary.close()


# ── Factory ───────────────────────────────────────────────────────────────


def create_llm_provider() -> LLMProvider:
    """Instantiate the LLM provider(s) based on LLM_PROVIDER config.

    Returns an LLMProvider ready to use.
    """
    mode = config.LLM_PROVIDER  # "local" | "cloud" | "auto"
    logger.info(f"LLM provider mode: {mode}")

    if mode == "local":
        return _make_local()

    if mode == "cloud":
        return _make_cloud()

    # mode == "auto": prefer local, fall back to cloud
    local = _make_local()
    from core.ai.ollama_provider import OllamaProvider

    if isinstance(local, OllamaProvider) and local.is_available():
        logger.info("Ollama is reachable — using local as primary with cloud fallback")
        cloud = _make_cloud()
        return FallbackProvider(primary=local, secondary=cloud)
    else:
        logger.info("Ollama not available — using cloud as primary with local fallback")
        cloud = _make_cloud()
        return FallbackProvider(primary=cloud, secondary=local)


def _make_local() -> LLMProvider:
    from core.ai.ollama_provider import OllamaProvider

    return OllamaProvider()


def _make_cloud() -> LLMProvider:
    from core.ai.openrouter import OpenRouterClient

    return OpenRouterClient()
