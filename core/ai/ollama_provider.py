"""Ollama local LLM provider for Max AI planner.

Uses a locally running Ollama server with phi3:mini (or other models)
to generate structured JSON action plans — fully offline, no API keys.
"""

import json
import logging
import time
from typing import Optional

import httpx

import config
from core.ai.llm_provider import LLMProvider
from core.ai.prompt import build_prompt_with_context
from core.ai.schema import validate_action_plan

logger = logging.getLogger(__name__)


class OllamaProvider(LLMProvider):
    """Local LLM provider using Ollama REST API."""

    def __init__(self):
        self.base_url = config.OLLAMA_BASE_URL
        self.model = config.OLLAMA_MODEL
        self.max_retries = 3
        self.num_ctx = config.OLLAMA_NUM_CTX
        self._client = httpx.Client(timeout=120.0)  # local inference can be slow

        logger.info(f"Ollama provider: model={self.model}, url={self.base_url}")

    @property
    def provider_name(self) -> str:
        return f"Ollama ({self.model})"

    # ── Health check ──────────────────────────────────────────────────────

    def is_available(self) -> bool:
        """Check if the Ollama server is reachable and model is loaded."""
        try:
            resp = self._client.get(f"{self.base_url}/api/tags", timeout=5.0)
            if resp.status_code != 200:
                return False
            models = [m["name"] for m in resp.json().get("models", [])]
            # Check both "phi3:mini" and "phi3:mini" style names
            base_model = self.model.split(":")[0]
            return any(base_model in m for m in models)
        except Exception:
            return False

    # ── Plan generation ───────────────────────────────────────────────────

    def plan(
        self,
        user_text: str,
        recent_conversations: list[dict] = None,
    ) -> Optional[dict]:
        """Convert user text to a validated action plan via Ollama.

        Args:
            user_text: The user's voice command (transcribed).
            recent_conversations: Recent history for context.

        Returns:
            Validated action plan dict, or None on failure.
        """
        messages = build_prompt_with_context(recent_conversations)
        messages.append({"role": "user", "content": user_text})

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"Ollama request (attempt {attempt}): {user_text[:100]}")
                response = self._client.post(
                    f"{self.base_url}/api/chat",
                    json={
                        "model": self.model,
                        "messages": messages,
                        "stream": False,
                        "format": "json",
                        "options": {
                            "temperature": 0,
                            "num_ctx": self.num_ctx,
                            "num_gpu": 99,  # offload all layers to GPU
                        },
                    },
                )

                if response.status_code != 200:
                    logger.error(
                        f"Ollama error {response.status_code}: {response.text[:300]}"
                    )
                    continue

                data = response.json()
                raw_content = data.get("message", {}).get("content", "")
                logger.info(f"Ollama raw output: {raw_content[:500]}")

                if not raw_content.strip():
                    logger.warning(f"Empty response on attempt {attempt}")
                    continue

                plan = validate_action_plan(raw_content)
                if plan is not None:
                    return plan

                logger.warning(f"Invalid plan on attempt {attempt}, retrying...")

            except httpx.TimeoutException:
                logger.warning(f"Ollama timeout on attempt {attempt}")
            except Exception as e:
                logger.error(f"Ollama request failed: {e}")

            if attempt < self.max_retries:
                time.sleep(0.5)

        logger.error("All Ollama attempts failed")
        return None

    # ── Cleanup ───────────────────────────────────────────────────────────

    def close(self):
        """Close the HTTP client."""
        self._client.close()
