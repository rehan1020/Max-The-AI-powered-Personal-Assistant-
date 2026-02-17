"""Browser control via Playwright + Chrome Remote Debugging.

Attaches to a real Chrome instance with user's profile, cookies, and sessions.
Chrome is launched with --remote-debugging-port for visible automation.
"""

import logging
import subprocess
import time
import asyncio
from typing import Optional
from pathlib import Path

import config

logger = logging.getLogger(__name__)


class BrowserController:
    """Controls the user's real Chrome browser via CDP."""

    def __init__(self):
        self._browser = None
        self._context = None
        self._page = None
        self._playwright = None
        self._chrome_process = None

    async def _ensure_playwright(self):
        """Lazy-import and start Playwright."""
        if self._playwright is None:
            from playwright.async_api import async_playwright
            self._playwright = await async_playwright().start()
            logger.info("Playwright started")

    def launch_chrome(self) -> bool:
        """Launch Chrome with remote debugging enabled."""
        try:
            chrome_path = config.CHROME_PATH
            port = config.CHROME_DEBUG_PORT
            user_data = config.CHROME_USER_DATA

            cmd = [
                chrome_path,
                f"--remote-debugging-port={port}",
                f"--user-data-dir={user_data}",
                "--no-first-run",
                "--no-default-browser-check",
            ]

            self._chrome_process = subprocess.Popen(
                cmd,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            logger.info(f"Chrome launched on debug port {port}")
            time.sleep(2)  # Wait for Chrome to start
            return True

        except FileNotFoundError:
            logger.error(f"Chrome not found at: {config.CHROME_PATH}")
            return False
        except Exception as e:
            logger.error(f"Failed to launch Chrome: {e}")
            return False

    async def connect(self) -> bool:
        """Connect Playwright to the running Chrome instance."""
        try:
            await self._ensure_playwright()
            cdp_url = f"http://localhost:{config.CHROME_DEBUG_PORT}"
            self._browser = await self._playwright.chromium.connect_over_cdp(cdp_url)

            contexts = self._browser.contexts
            if contexts:
                self._context = contexts[0]
                pages = self._context.pages
                if pages:
                    self._page = pages[0]
                else:
                    self._page = await self._context.new_page()
            else:
                self._context = await self._browser.new_context()
                self._page = await self._context.new_page()

            logger.info("Connected to Chrome via CDP")
            return True

        except Exception as e:
            logger.error(f"Failed to connect to Chrome: {e}")
            return False

    async def ensure_connected(self) -> bool:
        """Ensure we have a live connection to Chrome."""
        if self._page is None:
            self.launch_chrome()
            return await self.connect()

        try:
            await self._page.title()
            return True
        except Exception:
            logger.info("Connection lost, reconnecting...")
            return await self.connect()

    async def open_browser(self, **params) -> dict:
        """Open Chrome (launch if not running)."""
        self.launch_chrome()
        connected = await self.connect()
        return {
            "success": connected,
            "message": "Chrome opened" if connected else "Failed to open Chrome",
        }

    async def navigate(self, **params) -> dict:
        """Navigate to a URL."""
        url = params.get("url", "")
        if not url:
            return {"success": False, "message": "No URL provided"}

        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        if not await self.ensure_connected():
            return {"success": False, "message": "Not connected to Chrome"}

        try:
            await self._page.goto(url, wait_until="domcontentloaded", timeout=15000)
            title = await self._page.title()
            logger.info(f"Navigated to: {url} — Title: {title}")
            return {"success": True, "message": f"Navigated to {url}", "title": title}
        except Exception as e:
            logger.error(f"Navigation failed: {e}")
            return {"success": False, "message": f"Navigation failed: {e}"}

    async def click_element(self, **params) -> dict:
        """Click an element by selector, text, or coordinates."""
        if not await self.ensure_connected():
            return {"success": False, "message": "Not connected to Chrome"}

        try:
            if "selector" in params:
                await self._page.click(params["selector"], timeout=5000)
                return {"success": True, "message": f"Clicked: {params['selector']}"}
            elif "text" in params:
                await self._page.get_by_text(params["text"]).first.click(timeout=5000)
                return {"success": True, "message": f"Clicked text: {params['text']}"}
            elif "x" in params and "y" in params:
                await self._page.mouse.click(int(params["x"]), int(params["y"]))
                return {"success": True, "message": f"Clicked at ({params['x']}, {params['y']})"}
            else:
                return {"success": False, "message": "No click target specified"}
        except Exception as e:
            logger.error(f"Click failed: {e}")
            return {"success": False, "message": f"Click failed: {e}"}

    async def type_text(self, **params) -> dict:
        """Type text into the currently focused element."""
        text = params.get("text", "")
        if not await self.ensure_connected():
            return {"success": False, "message": "Not connected to Chrome"}

        try:
            await self._page.keyboard.type(text, delay=30)
            return {"success": True, "message": f"Typed: {text[:50]}"}
        except Exception as e:
            logger.error(f"Type failed: {e}")
            return {"success": False, "message": f"Type failed: {e}"}

    async def press_key(self, **params) -> dict:
        """Press a key or key combination in the browser."""
        key = params.get("key", "")
        if not await self.ensure_connected():
            return {"success": False, "message": "Not connected to Chrome"}

        try:
            # Convert common formats to Playwright format
            key_map = {
                "enter": "Enter",
                "tab": "Tab",
                "escape": "Escape",
                "backspace": "Backspace",
                "delete": "Delete",
                "ctrl+c": "Control+c",
                "ctrl+v": "Control+v",
                "ctrl+a": "Control+a",
                "ctrl+t": "Control+t",
                "ctrl+w": "Control+w",
                "alt+f4": "Alt+F4",
            }
            pw_key = key_map.get(key.lower(), key)
            await self._page.keyboard.press(pw_key)
            return {"success": True, "message": f"Pressed: {key}"}
        except Exception as e:
            logger.error(f"Key press failed: {e}")
            return {"success": False, "message": f"Key press failed: {e}"}

    async def search_web(self, **params) -> dict:
        """Search Google for a query."""
        query = params.get("query", "")
        if not query:
            return {"success": False, "message": "No search query provided"}

        url = f"https://www.google.com/search?q={query}"
        return await self.navigate(url=url)

    async def get_page_text(self) -> Optional[str]:
        """Get visible text content of the current page."""
        if not await self.ensure_connected():
            return None
        try:
            return await self._page.inner_text("body")
        except Exception:
            return None

    async def get_page_title(self) -> Optional[str]:
        """Get the title of the current page."""
        if not await self.ensure_connected():
            return None
        try:
            return await self._page.title()
        except Exception:
            return None

    async def close(self):
        """Clean up browser connections."""
        try:
            if self._browser:
                await self._browser.close()
            if self._playwright:
                await self._playwright.stop()
        except Exception:
            pass
        self._browser = None
        self._context = None
        self._page = None
        self._playwright = None
