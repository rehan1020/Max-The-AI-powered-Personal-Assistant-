"""Response cache for LLM plans.

File-backed cache to avoid LLM calls for repeated identical commands.
"""

import hashlib
import json
import time
from pathlib import Path
from typing import Optional


class ResponseCache:
    """File-backed LLM response cache."""

    def __init__(self, cache_path: Path, ttl: int = 3600):
        """Initialize the cache.
        
        Args:
            cache_path: Path to the cache file.
            ttl: Time-to-live in seconds for cached entries.
        """
        self._path = cache_path
        self._ttl = ttl
        self._data: dict = {}
        self._load()

    def get(self, command: str) -> Optional[dict]:
        """Get a cached plan for a command.
        
        Args:
            command: The user command to look up.
            
        Returns:
            The cached plan, or None if not found or expired.
        """
        key = self._hash(command)
        if key in self._data:
            plan, ts = self._data[key]
            if time.time() - ts < self._ttl:
                return plan
            del self._data[key]
        return None

    def set(self, command: str, plan: dict) -> None:
        """Cache a plan for a command.
        
        Args:
            command: The user command.
            plan: The action plan to cache.
        """
        key = self._hash(command)
        self._data[key] = (plan, time.time())
        self._save()

    def _hash(self, command: str) -> str:
        """Generate a hash for a command."""
        normalized = command.lower().strip()
        return hashlib.sha256(normalized.encode()).hexdigest()

    def _load(self) -> None:
        """Load cache from disk."""
        if self._path.exists():
            try:
                with open(self._path) as f:
                    self._data = json.load(f)
            except (json.JSONDecodeError, IOError):
                self._data = {}

    def _save(self) -> None:
        """Save cache to disk."""
        try:
            self._path.parent.mkdir(parents=True, exist_ok=True)
            with open(self._path, "w") as f:
                json.dump(self._data, f)
        except IOError:
            pass

    def clear(self) -> None:
        """Clear all cached entries."""
        self._data = {}
        self._save()

    def clear_expired(self) -> int:
        """Remove expired entries and return count of removed entries."""
        now = time.time()
        expired_keys = [
            k for k, (_, ts) in self._data.items()
            if now - ts >= self._ttl
        ]
        for k in expired_keys:
            del self._data[k]
        if expired_keys:
            self._save()
        return len(expired_keys)
