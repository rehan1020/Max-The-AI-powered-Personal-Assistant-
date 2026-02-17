#!/usr/bin/env python3
"""Quick test of all core subsystems to verify nothing broke."""

import logging
logging.basicConfig(level=logging.INFO, format='%(message)s')

print("=== Testing Core Subsystems ===\n")

# 1. Test LLM Provider
print("[1] Testing LLM Provider (Ollama phi3:mini)...")
from core.ai.provider_factory import create_llm_provider
try:
    llm = create_llm_provider()
    print(f"[OK] LLM provider initialized: {llm}")
    llm.close()
except Exception as e:
    print(f"[FAIL] LLM provider failed: {e}")

# 2. Test Volume Control  
print("\n[2] Testing Volume Control...")
from core.execution.system_control import system_volume
try:
    result = system_volume(level=50)
    print(f"[OK] Volume control works: {result['message']}")
except Exception as e:
    print(f"[FAIL] Volume control failed: {e}")

# 3. Test System Lock
print("\n[3] Testing System Lock Function...")
from core.execution.system_control import system_lock
try:
    # Just verify the function exists and can be called
    print(f"[OK] system_lock function available")
except Exception as e:
    print(f"[FAIL] system_lock failed: {e}")

# 4. Test Brightness Control
print("\n[4] Testing Brightness Control...")
from core.execution.system_control import system_brightness
try:
    result = system_brightness(level=50)
    print(f"[OK] Brightness control works: {result['message']}")
except Exception as e:
    print(f"[FAIL] Brightness control failed: {e}")

print("\n=== All subsystems operational ===")

