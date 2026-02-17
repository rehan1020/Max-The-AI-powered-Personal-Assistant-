"""Action Dispatcher — maps JSON action plans to Python handlers.

This is the core execution engine. It receives validated action plans
and executes each action through the appropriate handler.
NEVER executes raw AI output — only structured, validated actions.
"""

import asyncio
import logging
import time
from typing import Optional

import config
from core.execution.browser_control import BrowserController
from core.execution import mouse_keyboard
from core.execution import file_manager
from core.execution import system_control
from core.execution.screen_reader import ScreenReader

logger = logging.getLogger(__name__)


class ActionDispatcher:
    """Dispatches validated action plans to the correct handlers."""

    def __init__(self):
        self.browser = BrowserController()
        self.screen = ScreenReader()
        self._results = []
        self._event_loop = None

        # Map action types to handler functions
        self._handlers = {
            # Browser actions (async)
            "open_browser": self._exec_async(self.browser.open_browser),
            "navigate": self._exec_async(self.browser.navigate),
            "search_web": self._exec_async(self.browser.search_web),

            # Browser click/type (try browser first, fall back to pyautogui)
            "click": self._handle_click,
            "type_text": self._handle_type,
            "press_key": self._handle_press_key,

            # Mouse
            "move_mouse": lambda **p: mouse_keyboard.move_mouse(**p),

            # File operations
            "file_create": lambda **p: file_manager.file_create(**p),
            "file_delete": lambda **p: file_manager.file_delete(**p),
            "file_move": lambda **p: file_manager.file_move(**p),

            # System control
            "open_app": lambda **p: system_control.open_app(**p),
            "close_app": lambda **p: system_control.close_app(**p),
            "system_volume": lambda **p: system_control.system_volume(**p),
            "system_brightness": lambda **p: system_control.system_brightness(**p),
            "system_sleep": lambda **p: system_control.system_sleep(**p),
            "system_lock": lambda **p: system_control.system_lock(**p),
            "system_shutdown": lambda **p: system_control.system_shutdown(**p),
            "system_restart": lambda **p: system_control.system_restart(**p),
            "system_wifi": lambda **p: system_control.system_wifi(**p),
            "system_bluetooth": lambda **p: system_control.system_bluetooth(**p),
            "system_screensaver": lambda **p: system_control.system_screensaver(**p),
            "system_mute": lambda **p: system_control.system_mute(**p),
            "system_unmute": lambda **p: system_control.system_unmute(**p),
            "install_software": lambda **p: system_control.install_software(**p),

            # Screen reading
            "read_screen": lambda **p: self.screen.read_screen(**p),
            "summarize_screen": lambda **p: self.screen.summarize_screen(**p),

            # Utility
            "wait": self._handle_wait,
        }

    def _get_event_loop(self):
        """Get or create an event loop for async operations."""
        if self._event_loop is None or self._event_loop.is_closed():
            try:
                self._event_loop = asyncio.get_running_loop()
            except RuntimeError:
                self._event_loop = asyncio.new_event_loop()
                asyncio.set_event_loop(self._event_loop)
        return self._event_loop

    def _exec_async(self, async_func):
        """Wrap an async function for synchronous execution."""
        def wrapper(**params):
            loop = self._get_event_loop()
            if loop.is_running():
                # If we're already in an async context, create a task
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as pool:
                    future = pool.submit(asyncio.run, async_func(**params))
                    return future.result(timeout=30)
            else:
                return loop.run_until_complete(async_func(**params))
        return wrapper

    def execute_plan(self, plan: dict, skip_indices: set = None) -> list[dict]:
        """Execute all actions in a plan sequentially.
        
        Args:
            plan: Validated action plan dict.
            skip_indices: Set of action indices to skip (e.g., blocked ones).
        
        Returns:
            List of result dicts for each action.
        """
        skip_indices = skip_indices or set()
        results = []

        actions = plan.get("actions", [])
        logger.info(f"Executing plan: {plan['task_type']} with {len(actions)} actions")

        for i, action in enumerate(actions):
            if i in skip_indices:
                results.append({
                    "action_index": i,
                    "action_type": action["type"],
                    "success": False,
                    "message": "Skipped (blocked or denied)",
                    "skipped": True,
                })
                continue

            action_type = action["type"]
            params = action.get("parameters", {})

            logger.info(f"Executing action {i+1}/{len(actions)}: {action_type}")
            start_time = time.time()

            try:
                handler = self._handlers.get(action_type)
                if handler is None:
                    result = {"success": False, "message": f"No handler for: {action_type}"}
                else:
                    result = handler(**params)

                elapsed = time.time() - start_time
                result["action_index"] = i
                result["action_type"] = action_type
                result["elapsed_seconds"] = round(elapsed, 2)
                results.append(result)

                logger.info(
                    f"Action {i+1} ({action_type}): "
                    f"{'OK' if result.get('success') else 'FAIL'} "
                    f"({elapsed:.2f}s) — {result.get('message', '')}"
                )

                # If an action fails, stop execution 
                if not result.get("success", False):
                    logger.warning(f"Action {i+1} failed — stopping plan execution")
                    # Mark remaining actions as skipped
                    for j in range(i + 1, len(actions)):
                        results.append({
                            "action_index": j,
                            "action_type": actions[j]["type"],
                            "success": False,
                            "message": "Skipped (previous action failed)",
                            "skipped": True,
                        })
                    break

            except Exception as e:
                elapsed = time.time() - start_time
                logger.error(f"Action {i+1} ({action_type}) exception: {e}")
                results.append({
                    "action_index": i,
                    "action_type": action_type,
                    "success": False,
                    "message": f"Exception: {e}",
                    "elapsed_seconds": round(elapsed, 2),
                })
                break

        self._results = results
        return results

    def _handle_click(self, **params) -> dict:
        """Handle click — try browser DOM first, fall back to pyautogui."""
        if "selector" in params or "text" in params:
            # Try browser click
            try:
                return self._exec_async(self.browser.click_element)(**params)
            except Exception:
                pass

        # Fall back to pyautogui
        return mouse_keyboard.click(**params)

    def _handle_type(self, **params) -> dict:
        """Handle type — try browser first, fall back to pyautogui."""
        try:
            return self._exec_async(self.browser.type_text)(**params)
        except Exception:
            return mouse_keyboard.type_text(**params)

    def _handle_press_key(self, **params) -> dict:
        """Handle key press — try browser first, fall back to pyautogui."""
        try:
            return self._exec_async(self.browser.press_key)(**params)
        except Exception:
            return mouse_keyboard.press_key(**params)

    def _handle_wait(self, **params) -> dict:
        """Handle wait action."""
        seconds = float(params.get("seconds", 1))
        message = params.get("message", "")
        time.sleep(seconds)
        return {
            "success": True,
            "message": message or f"Waited {seconds}s",
        }

    def get_last_results(self) -> list[dict]:
        """Get results of the last executed plan."""
        return self._results

    async def cleanup(self):
        """Clean up resources."""
        await self.browser.close()
