"""OpenRouter API client for Max AI planner.

Sends user commands to OpenRouter and receives structured JSON plans.
Uses the free tier model by default.  Implements the LLMProvider interface.
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

OPENROUTER_CHAT_URL = f"{config.OPENROUTER_BASE_URL}/chat/completions"


class OpenRouterClient(LLMProvider):
    """Client for OpenRouter API — converts text commands to action plans."""

    def __init__(self):
        self.api_key = config.OPENROUTER_API_KEY
        self.model = config.OPENROUTER_MODEL
        self.max_retries = 3
        self._client = httpx.Client(timeout=30.0)

        if not self.api_key:
            logger.error("OPENROUTER_API_KEY not set!")

    @property
    def provider_name(self) -> str:
        return f"OpenRouter ({self.model})"

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
        messages = build_prompt_with_context(recent_conversations)
        messages.append({"role": "user", "content": user_text})

        for attempt in range(1, self.max_retries + 1):
            try:
                logger.info(f"OpenRouter request (attempt {attempt}): {user_text[:100]}")
                response = self._client.post(
                    OPENROUTER_CHAT_URL,
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                        "HTTP-Referer": "https://max-desktop-agent.local",
                        "X-Title": "Max Desktop Agent",
                    },
                    json={
                        "model": self.model,
                        "messages": messages,
                        "temperature": 0.1,
                        "max_tokens": 1024,
                        "response_format": {"type": "json_object"},
                    },
                )

                if response.status_code == 429:
                    wait_time = min(2 ** attempt, 10)
                    logger.warning(f"Rate limited. Waiting {wait_time}s...")
                    time.sleep(wait_time)
                    continue

                if response.status_code != 200:
                    logger.error(f"OpenRouter error {response.status_code}: {response.text[:300]}")
                    continue

                data = response.json()
                raw_content = data["choices"][0]["message"]["content"] or ""
                logger.info(f"AI raw output: {raw_content[:500]}")

                plan = validate_action_plan(raw_content)
                if plan is not None:
                    return plan

                logger.warning(f"Invalid plan on attempt {attempt}, retrying...")

            except httpx.TimeoutException:
                logger.warning(f"OpenRouter timeout on attempt {attempt}")
            except Exception as e:
                logger.error(f"OpenRouter request failed: {e}")

            if attempt < self.max_retries:
                time.sleep(1)

        logger.error("All OpenRouter attempts failed")
        return None

    def close(self):
        """Close the HTTP client."""
        self._client.close()
