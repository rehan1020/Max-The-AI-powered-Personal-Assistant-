"""Tests for response cache."""

import pytest
import time
from pathlib import Path
from core.ai.response_cache import ResponseCache


class TestResponseCache:
    """Tests for the response cache."""

    def test_cache_set_and_get(self, temp_cache):
        """Test setting and getting cache entries."""
        cache = ResponseCache(temp_cache, ttl=3600)
        
        command = "open chrome"
        plan = {"task_type": "single_step", "actions": [{"type": "open_browser"}]}
        
        cache.set(command, plan)
        result = cache.get(command)
        
        assert result is not None
        assert result["actions"][0]["type"] == "open_browser"

    def test_cache_miss(self, temp_cache):
        """Test cache miss returns None."""
        cache = ResponseCache(temp_cache)
        
        result = cache.get("nonexistent command")
        assert result is None

    def test_cache_expiry(self, temp_cache):
        """Test cache expiry after TTL."""
        cache = ResponseCache(temp_cache, ttl=1)
        
        command = "open chrome"
        plan = {"task_type": "single_step", "actions": [{"type": "open_browser"}]}
        
        cache.set(command, plan)
        time.sleep(1.5)
        
        result = cache.get(command)
        assert result is None

    def test_cache_clear(self, temp_cache):
        """Test clearing cache."""
        cache = ResponseCache(temp_cache)
        
        cache.set("command 1", {"actions": []})
        cache.set("command 2", {"actions": []})
        
        cache.clear()
        
        assert cache.get("command 1") is None
        assert cache.get("command 2") is None

    def test_case_insensitive(self, temp_cache):
        """Test cache is case insensitive."""
        cache = ResponseCache(temp_cache)
        
        plan = {"task_type": "single_step"}
        
        cache.set("Open Chrome", plan)
        result = cache.get("open chrome")
        
        assert result is not None
