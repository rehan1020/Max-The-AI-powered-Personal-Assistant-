#!/usr/bin/env python3
"""Test new safety and rule-based features."""

import json
from core.ai.rule_parser import parse_simple_command
from core.ai.plan_validator import PlanValidator, detect_complexity
import config

print("=" * 60)
print("TESTING RULE-BASED PARSER")
print("=" * 60)

simple_commands = [
    "open notepad",
    "set volume to 50",
    "lock the screen",
    "turn wifi off",
    "set brightness to 75",
    "mute",
    "open chrome",
]

for cmd in simple_commands:
    plan = parse_simple_command(cmd)
    if plan:
        actions = [a["type"] for a in plan.get("actions", [])]
        print(f"✓ '{cmd}'")
        print(f"  → {actions}\n")
    else:
        print(f"✗ '{cmd}' — no rule matched\n")

print("\n" + "=" * 60)
print("TESTING PLAN VALIDATOR")
print("=" * 60)

# Test valid plan
valid_plan = {
    "task_type": "single_step",
    "requires_confirmation": False,
    "actions": [
        {
            "type": "open_app",
            "parameters": {"name": "notepad"}
        }
    ]
}

validator = PlanValidator()
is_valid, error, complexity, concerns = validator.validate(valid_plan)
print(f"Valid simple plan: {is_valid} (complexity={complexity})")
if concerns:
    print(f"  Concerns: {concerns}")

# Test complex plan
complex_plan = {
    "task_type": "multi_step",
    "requires_confirmation": False,
    "actions": [
        {"type": "open_browser", "parameters": {"browser": "chrome"}},
        {"type": "navigate", "parameters": {"url": "https://google.com"}},
        {"type": "type_text", "parameters": {"text": "hello"}},
        {"type": "press_key", "parameters": {"key": "enter"}},
        {"type": "wait", "parameters": {"seconds": 2}},
    ]
}

is_valid, error, complexity, concerns = validator.validate(complex_plan)
print(f"\nComplex plan (5 actions): {is_valid} (complexity={complexity})")
if concerns:
    print(f"  Concerns: {concerns}")

# Test dangerous plan
dangerous_plan = {
    "task_type": "multi_step",
    "requires_confirmation": False,
    "actions": [
        {"type": "system_shutdown", "parameters": {"delay": 60}},
        {"type": "file_delete", "parameters": {"path": "C:/important.txt"}},
    ]
}

is_valid, error, complexity, concerns = validator.validate(dangerous_plan)
print(f"\nDangerous plan (shutdown + delete): {is_valid} (complexity={complexity})")
if concerns:
    print(f"  Concerns: {concerns}")

# Test invalid plan
invalid_plan = {
    "task_type": "single_step",
    "actions": [
        {"type": "invalid_action", "parameters": {}}
    ]
}

is_valid, error, complexity, concerns = validator.validate(invalid_plan)
print(f"\nInvalid plan: {is_valid}")
if error:
    print(f"  Error: {error}")

print("\n" + "=" * 60)
print("TESTING SAFETY MODES")
print("=" * 60)

print(f"SIMPLE_COMMANDS_ONLY: {config.SIMPLE_COMMANDS_ONLY}")
print(f"REQUIRE_CONFIRMATION_FOR_DANGEROUS: {config.REQUIRE_CONFIRMATION_FOR_DANGEROUS}")
print(f"REJECT_COMPLEX_PLANS: {config.REJECT_COMPLEX_PLANS}")
print(f"MAX_ACTIONS_PER_PLAN: {config.MAX_ACTIONS_PER_PLAN}")

print("\n" + "=" * 60)
print("All tests completed!")
print("=" * 60)
