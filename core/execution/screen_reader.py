"""Screen reading — screenshots and OCR.

Uses mss for fast screenshots and easyocr for text extraction.
Can also send screenshots to OpenRouter for visual understanding.
"""

import io
import logging
import base64
from typing import Optional

import numpy as np

logger = logging.getLogger(__name__)


class ScreenReader:
    """Captures and reads screen content."""

    def __init__(self):
        self._ocr_reader = None

    def _ensure_ocr(self):
        """Lazy-load EasyOCR reader."""
        if self._ocr_reader is None:
            import easyocr
            self._ocr_reader = easyocr.Reader(["en"], gpu=True)
            logger.info("EasyOCR initialized")

    def take_screenshot(self, region: dict = None) -> Optional[np.ndarray]:
        """Take a screenshot, optionally of a specific region.
        
        Args:
            region: dict with x, y, width, height keys, or None for full screen.
        
        Returns:
            numpy array (BGR format), or None on failure.
        """
        try:
            import mss
            with mss.mss() as sct:
                if region:
                    monitor = {
                        "left": int(region.get("x", 0)),
                        "top": int(region.get("y", 0)),
                        "width": int(region.get("width", 1920)),
                        "height": int(region.get("height", 1080)),
                    }
                else:
                    monitor = sct.monitors[1]  # Primary monitor

                screenshot = sct.grab(monitor)
                img = np.array(screenshot)
                logger.debug(f"Screenshot captured: {img.shape}")
                return img
        except Exception as e:
            logger.error(f"Screenshot failed: {e}")
            return None

    def screenshot_to_base64(self, region: dict = None) -> Optional[str]:
        """Take a screenshot and return as base64 PNG string."""
        img = self.take_screenshot(region)
        if img is None:
            return None

        try:
            from PIL import Image
            pil_img = Image.fromarray(img[:, :, :3])  # Drop alpha channel
            buffer = io.BytesIO()
            pil_img.save(buffer, format="PNG", optimize=True)
            b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")
            return b64
        except ImportError:
            # Fallback without PIL — use mss built-in
            try:
                import mss
                import mss.tools
                with mss.mss() as sct:
                    monitor = sct.monitors[1]
                    screenshot = sct.grab(monitor)
                    png_bytes = mss.tools.to_png(screenshot.rgb, screenshot.size)
                    return base64.b64encode(png_bytes).decode("utf-8")
            except Exception as e:
                logger.error(f"Screenshot to base64 failed: {e}")
                return None

    def read_screen_text(self, region: dict = None) -> Optional[str]:
        """OCR the screen and return extracted text."""
        img = self.take_screenshot(region)
        if img is None:
            return None

        try:
            self._ensure_ocr()
            # EasyOCR expects RGB
            rgb_img = img[:, :, :3]  # Drop alpha if present
            results = self._ocr_reader.readtext(rgb_img)

            texts = [text for (_, text, conf) in results if conf > 0.3]
            full_text = " ".join(texts)
            logger.info(f"OCR extracted {len(texts)} text regions")
            return full_text if full_text else None
        except Exception as e:
            logger.error(f"OCR failed: {e}")
            return None

    def read_screen(self, **params) -> dict:
        """Action handler: read screen content."""
        region_type = params.get("region", "full")

        if region_type == "area" and all(k in params for k in ("x", "y", "width", "height")):
            region = {
                "x": params["x"],
                "y": params["y"],
                "width": params["width"],
                "height": params["height"],
            }
        else:
            region = None

        text = self.read_screen_text(region)
        if text:
            return {"success": True, "message": f"Screen text: {text[:500]}", "text": text}
        return {"success": False, "message": "Could not read screen text"}

    def summarize_screen(self, **params) -> dict:
        """Action handler: take screenshot for AI summarization."""
        b64 = self.screenshot_to_base64()
        if b64:
            return {
                "success": True,
                "message": "Screenshot captured for summarization",
                "screenshot_b64": b64,
            }
        return {"success": False, "message": "Failed to capture screenshot"}
