# Safety & Control Architecture Guide

This document describes the new safety and control improvements implemented based on architectural best practices for AI agents.

---

## 🛡️ Safety Layers

Max implements a defense-in-depth strategy to ensure that AI-generated actions are safe for your system.

### 1. Path Protection (Hardened)
Max cannot touch sensitive system directories or its own source code. This is enforced at the `core/safety/validator.py` level.
- **Protected Paths**: `C:\Windows`, `C:\Program Files`, and the project's own directory.
- **Self-Modification Block**: AI attempts to edit `.py` files in the project root are automatically blocked.

### 2. Action Classification
Every action is categorized before execution:
- **✅ SAFE**: (e.g., `open_app`, `navigate`, `read_screen`) Executed instantly.
- **⚠️ DANGEROUS**: (e.g., `file_delete`, `install_software`, `system_shutdown`) Requires manual user confirmation in the GUI when **Safe Mode** is ON.
- **🚫 BLOCKED**: (e.g., `eval()`, direct shell access) These are not supported by the dispatcher and will be rejected.

### 3. URL & Key Validation
- **URL Filtering**: Blocks `javascript:`, `data:`, and `file:///` protocols in browser commands.
- **Restricted Keys**: Destructive combinations like `Alt+F4` or `Ctrl+Alt+Del` are flagged as dangerous.

## ⚙️ Configuration

You can tune safety settings in `config.py`:
- `SAFE_MODE`: Default `True`. Toggle via GUI.
- `PROTECTED_PATHS`: List of absolute paths that Max is forbidden from modifying.

---

## 🏗️ Architecture Overview

Max now uses a **multi-layer safety and control system**:

```
User Command
    ↓
[1] Rule-Based Parser (deterministic, fast, safe)
    ↓
  Match found? → Direct execution
  ↓
  No match → Check SIMPLE_COMMANDS_ONLY
    ↓
  YES (reject) → "I only handle simple commands"
  ↓
  NO → Continue to LLM
    ↓
[2] LLM Planner (uses phi3:mini locally)
    ↓
[3] Plan Validator (schema + complexity + safety)
    ↓
[4] Dangerous Action Whitelist Check
    ↓
[5] User Confirmation (if needed)
    ↓
[6] Execution Engine
    ↓
[7] Result Feedback
```

---

## 1️⃣ Rule-Based Parser

**Location:** `core/ai/rule_parser.py`

The rule-based parser intercepts common commands and converts them to action plans **without invoking the LLM**.

### Benefits:
- ⚡ **Fast** — No network calls, instant response
- 🔒 **Safe** — Deterministic, predictable output
- 💰 **Cheap** — No API costs or token usage
- 🎯 **Accurate** — No model hallucination

### How It Works:

```python
# User says: "set volume to 50"
# Parser matches regex: r"^set\s+(?:the\s+)?volume\s+to\s+(\d+)"
# Returns:
{
  "task_type": "single_step",
  "actions": [
    {"type": "system_volume", "parameters": {"level": 50}}
  ]
}
```

### Supported Commands:

- **App launching:** "open notepad", "launch chrome", "start firefox"
- **System control:** "mute", "lock screen", "sleep"
- **Volume:** "set volume to 50", "mute", "unmute"
- **Brightness:** "set brightness to 75"
- **Power:** "shutdown", "restart", "lock"
- **WiFi/Bluetooth:** "turn wifi on", "toggle bluetooth"

**To add new rules:** Edit `SIMPLE_COMMAND_RULES` dict in `rule_parser.py`

---

## 2️⃣ JSON Schema Validation

**Location:** `core/ai/plan_validator.py`

Validates that all LLM-generated plans conform to the expected structure.

### What It Checks:

✓ Plan has required fields (`task_type`, `actions`)  
✓ `task_type` is valid (`single_step`, `multi_step`, `clarify`)  
✓ Each action has valid `type` and `parameters`  
✓ No unknown action types  
✓ Parameters are dicts (not strings or lists)  

### Example:

```python
from core.ai.plan_validator import validate_plan_schema

plan = {"task_type": "single_step", ...}
is_valid, error = validate_plan_schema(plan)

if not is_valid:
    print(f"Invalid: {error}")
    # "Invalid: Missing required field: actions"
```

---

## 3️⃣ Complexity Detection

**Location:** `core/ai/plan_validator.py`

Automatically detects complexity and potential safety issues.

### Complexity Scoring:

- **Score 0 (Simple):** Single action, no dangerous ops
- **Score 1 (Moderate):** Multiple actions (2-5)
- **Score 2 (Complex):** 5+ actions, or contains dangerous actions, or loops

### Detected Concerns:

```python
complexity, concerns = detect_complexity(plan)

# Possible concerns:
# - "Multiple actions (5)"
# - "Contains 2 dangerous action(s)"
# - "Long sequence with waits (potential loop)"
# - "Contains conditional logic"
```

### Usage in Orchestrator:

If `REJECT_COMPLEX_PLANS=true`, Max rejects any plan with complexity score > 0.

---

## 4️⃣ Dangerous Action Whitelist

**Location:** `config.py`

Actions that ALWAYS require user confirmation:

```python
DANGEROUS_ACTIONS_WHITELIST = {
    "install_software",
    "file_delete",
    "system_shutdown",
    "system_restart",
}
```

If a plan contains ANY of these actions, **manual approval is required** before execution.

---

## 5️⃣ Configuration: Safety Modes

**Location:** `.env` file

### New Config Options:

```bash
# Only allow simple, rule-based commands (no LLM)
SIMPLE_COMMANDS_ONLY=false

# Require confirmation for ALL dangerous actions
REQUIRE_CONFIRMATION_FOR_DANGEROUS=true

# Reject any complex (multi-step) plans
REJECT_COMPLEX_PLANS=false

# Maximum actions per plan
MAX_ACTIONS_PER_PLAN=10
```

### Use Cases:

**🔒 Maximum Security (Kiosk/Public PC):**
```
SIMPLE_COMMANDS_ONLY=true
REQUIRE_CONFIRMATION_FOR_DANGEROUS=true
REJECT_COMPLEX_PLANS=true
MAX_ACTIONS_PER_PLAN=3
```

**⚙️ Power User (Home PC):**
```
SIMPLE_COMMANDS_ONLY=false
REQUIRE_CONFIRMATION_FOR_DANGEROUS=true
REJECT_COMPLEX_PLANS=false
MAX_ACTIONS_PER_PLAN=20
```

**🛡️ Balanced (Default):**
```
SIMPLE_COMMANDS_ONLY=false
REQUIRE_CONFIRMATION_FOR_DANGEROUS=true
REJECT_COMPLEX_PLANS=false
MAX_ACTIONS_PER_PLAN=10
```

---

## 6️⃣ Plan Sanitization

**Location:** `core/ai/plan_validator.py`

Before execution, dangerous actions are sanitized:

- 🗑️ **File Delete:** Blocks paths like `/`, `C:\`, `C:`
- 📦 **Install:** Removes shell metacharacters (`;`, `|`, `&`, etc.)
- 🔌 **Shutdown:** Caps delay to 1 hour max
- 🌐 **WiFi/Bluetooth:** Validated parameters

---

## 7️⃣ Orchestrator Integration

**Location:** `core/orchestrator.py`

New phases in the execution pipeline:

```
Phase 1: Transcribe ↓
Phase 2: Extract command ↓
Phase 3: Parse with rule-based parser ↓
Phase 4: [If no rule match] Use LLM ↓
Phase 5: Validate schema + complexity ↓
Phase 6: Sanitize actions ↓
Phase 7: Safety validation ↓
Phase 8: Confirmation [if needed] ↓
Phase 9: Execute ↓
Phase 10: Respond ↓
Phase 11: Save to memory
```

### Key Changes:

```python
# Before LLM is even called, try rule parser
plan = parse_simple_command(command)

if plan is None:
    # Only use LLM if no simple rule matched AND allowed
    if config.SIMPLE_COMMANDS_ONLY:
        reject("Complex commands not allowed")
    plan = self.ai.plan(command)

# Validate everything
is_valid, error, complexity, concerns = self.validator.validate(plan)
if not is_valid:
    reject(error)

# Sanitize dangerous actions
plan = self.validator.sanitize_plan(plan)
```

---

## 🧪 Testing

### Run Safety Feature Tests:

```bash
.\venv\Scripts\python.exe test_safety_features.py
```

Output shows:
- ✓ All rule-based commands parsed correctly
- ✓ Schema validation working
- ✓ Complexity detection accurate
- ✓ Safety modes configured

### Test Results Example:

```
✓ 'open notepad'
  → ['open_app']

✓ 'set volume to 50'
  → ['system_volume']

Valid simple plan: True (complexity=0)
Complex plan: True (complexity=2)
  Concerns: ['Multiple actions (5)', 'Long sequence with waits']
```

---

## 🎯 Usage Examples

### Example 1: Simple Command (Rule-Based)

```
User: "Mute the audio"

→ Rule parser matches: r"^mute|silence"
→ Returns: {"task_type": "single_step", "actions": [{"type": "system_volume", "parameters": {"action": "mute"}}]}
→ No LLM call
→ No confirmation
→ Instant execution ⚡
```

### Example 2: Complex Command (LLM + Validation)

```
User: "Open Chrome, go to YouTube, and search for Python"

→ Rule parser: No match (too complex)
→ Check SIMPLE_COMMANDS_ONLY: false (allowed)
→ LLM generates multi-step plan
→ Validator checks: complexity=2 (multiple actions)
→ Sanitizes parameters
→ Safety check: no dangerous actions
→ Confirms with user? No (safe action)
→ Executes all 3 actions
```

### Example 3: Dangerous Command (Requires Confirmation)

```
User: "Delete the file C:\important.txt"

→ Rule parser: No match
→ LLM generates plan: {"actions": [{"type": "file_delete", ...}]}
→ Validator detects: dangerous action in whitelist
→ REQUIRES_CONFIRMATION_FOR_DANGEROUS=true
→ Shows confirmation dialog: "Delete C:\important.txt?"
→ Wait for user approval
→ If approved: Execute
→ If denied: Cancel
```

### Example 4: Security Mode (Kiosk)

```
Config: SIMPLE_COMMANDS_ONLY=true

User: "Open Chrome and go to YouTube"

→ Rule parser: No match (too complex)
→ Check SIMPLE_COMMANDS_ONLY: true
→ Reject! "I only handle simple commands"
→ Only allow: "open chrome", "mute", "set volume", etc.
```

---

## 📊 Performance Impact

| Feature | Overhead | Notes |
|---------|----------|-------|
| Rule Parser | < 1ms | Regex matching, instant |
| Schema Validation | 1-2ms | Dict traversal |
| Complexity Detection | 1ms | String scanning |
| Sanitization | < 1ms | Parameter filtering |
| **Total overhead** | **3-5ms** | Negligible compared to LLM calls (1-5s) |

---

## 🔐 Security Guarantees

✅ **No arbitrary code execution** — All actions pre-defined  
✅ **No infinite loops** — Max 10 actions per plan by default  
✅ **No unauthorized file access** — Dangerous paths blocked  
✅ **No shell metacharacters** — Injection attempts sanitized  
✅ **Confirmation gates** — User approves high-impact actions  
✅ **Audit trail** — All commands logged to memory  

---

## 📝 Future Improvements

1. **Vector store for memory** — Sliding window + relevance threshold
2. **Task preview UI** — Show all actions before executing
3. **Undo support** — Reverse file moves, deletions
4. **More rule patterns** — Expand simple command coverage
5. **Rate limiting** — Throttle rapid dangerous commands
6. **Action history** — User can review past commands

---

## Quick Reference

| Config | Effect |
|--------|--------|
| `SIMPLE_COMMANDS_ONLY=true` | Block LLM, only rule-based |
| `REQUIRE_CONFIRMATION_FOR_DANGEROUS=true` | Approve dangerous actions |
| `REJECT_COMPLEX_PLANS=true` | Block multi-step commands |
| `MAX_ACTIONS_PER_PLAN=5` | Limit action sequences |

For more details, see `COMMANDS.md` for user command examples.
