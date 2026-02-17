"""File manager — safe file operations with protection enforcement.

All operations respect the protected paths list from config.
Max CANNOT modify its own project directory.
"""

import logging
import os
import shutil
from pathlib import Path

import config

logger = logging.getLogger(__name__)


def _is_protected(path_str: str) -> bool:
    """Check if a path falls within a protected directory."""
    try:
        path = Path(path_str).resolve()
        for protected in config.PROTECTED_PATHS:
            protected = Path(protected).resolve()
            try:
                path.relative_to(protected)
                logger.warning(f"Path is protected: {path_str}")
                return True
            except ValueError:
                continue
    except Exception:
        return True  # If we can't resolve, block it
    return False


def file_create(**params) -> dict:
    """Create a file with given content."""
    path_str = params.get("path", "")
    content = params.get("content", "")

    if not path_str:
        return {"success": False, "message": "No path provided"}

    if _is_protected(path_str):
        return {"success": False, "message": f"Protected path: {path_str}"}

    try:
        path = Path(path_str)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")
        logger.info(f"File created: {path_str}")
        return {"success": True, "message": f"Created: {path_str}"}
    except Exception as e:
        logger.error(f"File create failed: {e}")
        return {"success": False, "message": f"File create failed: {e}"}


def file_delete(**params) -> dict:
    """Delete a file or directory."""
    path_str = params.get("path", "")

    if not path_str:
        return {"success": False, "message": "No path provided"}

    if _is_protected(path_str):
        return {"success": False, "message": f"Protected path: {path_str}"}

    try:
        path = Path(path_str)
        if not path.exists():
            return {"success": False, "message": f"Path not found: {path_str}"}

        if path.is_file():
            path.unlink()
        elif path.is_dir():
            shutil.rmtree(path)
        else:
            return {"success": False, "message": f"Unknown path type: {path_str}"}

        logger.info(f"Deleted: {path_str}")
        return {"success": True, "message": f"Deleted: {path_str}"}
    except Exception as e:
        logger.error(f"File delete failed: {e}")
        return {"success": False, "message": f"File delete failed: {e}"}


def file_move(**params) -> dict:
    """Move/rename a file or directory."""
    source = params.get("source", "")
    destination = params.get("destination", "")

    if not source or not destination:
        return {"success": False, "message": "Source and destination required"}

    if _is_protected(source) or _is_protected(destination):
        return {"success": False, "message": "Protected path involved"}

    try:
        src_path = Path(source)
        if not src_path.exists():
            return {"success": False, "message": f"Source not found: {source}"}

        dst_path = Path(destination)
        dst_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.move(str(src_path), str(dst_path))

        logger.info(f"Moved: {source} → {destination}")
        return {"success": True, "message": f"Moved: {source} → {destination}"}
    except Exception as e:
        logger.error(f"File move failed: {e}")
        return {"success": False, "message": f"File move failed: {e}"}
