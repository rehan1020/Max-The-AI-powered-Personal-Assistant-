"""Tests for LLM command generation.

Converted from standalone script to proper pytest tests.
Uses a real or mock LLM provider depending on environment.
"""

import pytest
from core.ai.provider_factory import create_llm_provider

@pytest.fixture(scope="module")
def llm():
    provider = create_llm_provider()
    yield provider
    provider.close()

@pytest.mark.parametrize("cmd", [
    "Open WhatsApp",
    "Open Discord",
    "Open Calculator",
    "Open Firefox",
    "Search for cats on Google",
])
def test_llm_generates_actions(llm, cmd):
    """Test that the LLM generates a valid plan with actions for common commands."""
    plan = llm.plan(cmd)
    
    assert plan is not None, f"LLM returned None for command: '{cmd}'"
    assert "actions" in plan, f"Plan missing 'actions' for command: '{cmd}'"
    assert len(plan["actions"]) > 0, f"Plan has no actions for command: '{cmd}'"
    
    action_types = [a.get("type") for a in plan["actions"]]
    assert len(action_types) > 0
    
    # Basic sanity checks on action types
    if "Open" in cmd:
        assert any(t in ["open_app", "open_browser"] for t in action_types)
    if "Search" in cmd:
        assert any(t in ["open_browser", "search_web", "navigate"] for t in action_types)
