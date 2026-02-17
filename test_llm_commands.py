#!/usr/bin/env python3
"""Test LLM command generation with simplified prompt."""

import json
from core.ai.provider_factory import create_llm_provider

llm = create_llm_provider()

# Test cases to verify LLM generates correct actions
test_commands = [
    "Open WhatsApp",
    "Open Discord",
    "Open Calculator",
    "Open Firefox",
    "Search for cats on Google",
]

print("=== Testing LLM Command Generation ===\n")

for cmd in test_commands:
    try:
        # plan() returns a dict, not a string
        plan = llm.plan(cmd)
        
        if plan is None:
            print(f"Command: '{cmd}'")
            print(f"  ERROR: LLM returned None")
            print()
            continue
        
        action_types = [a.get("type") for a in plan.get("actions", [])]
        
        print(f"Command: '{cmd}'")
        print(f"  Actions: {action_types}")
        print(f"  Task Type: {plan.get('task_type')}")
        print()
    except Exception as e:
        print(f"Command: '{cmd}'")
        print(f"  ERROR: {e}")
        print()

llm.close()
