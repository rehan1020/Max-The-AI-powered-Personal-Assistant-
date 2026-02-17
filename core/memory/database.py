"""SQLite memory system — persistent conversation and preference storage.

Tables:
  - conversations: stores every interaction with timestamp, text, plan, result
  - preferences: key-value store for user preferences and context
"""

import json
import logging
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Optional

import config

logger = logging.getLogger(__name__)


class MemoryDatabase:
    """Persistent memory for Max using SQLite."""

    def __init__(self, db_path: Path = None):
        self.db_path = db_path or config.DB_PATH
        self._conn: Optional[sqlite3.Connection] = None
        self._init_db()

    def _init_db(self):
        """Initialize database and create tables if needed."""
        try:
            self._conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
            self._conn.row_factory = sqlite3.Row
            self._conn.execute("PRAGMA journal_mode=WAL")
            self._conn.execute("PRAGMA foreign_keys=ON")

            self._conn.executescript("""
                CREATE TABLE IF NOT EXISTS conversations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    user_text TEXT NOT NULL,
                    action_json TEXT,
                    result TEXT,
                    success INTEGER DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS preferences (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_conversations_timestamp 
                    ON conversations(timestamp DESC);
            """)
            self._conn.commit()
            logger.info(f"Memory database initialized: {self.db_path}")
        except Exception as e:
            logger.error(f"Failed to initialize database: {e}")

    def save_conversation(
        self,
        user_text: str,
        action_json: str = None,
        result: str = None,
        success: bool = False,
    ):
        """Save a conversation interaction."""
        try:
            self._conn.execute(
                """INSERT INTO conversations (timestamp, user_text, action_json, result, success)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    datetime.now().isoformat(),
                    user_text,
                    action_json,
                    result,
                    1 if success else 0,
                ),
            )
            self._conn.commit()
            logger.debug(f"Saved conversation: {user_text[:50]}")
        except Exception as e:
            logger.error(f"Failed to save conversation: {e}")

    def get_recent_conversations(self, limit: int = 5) -> list[dict]:
        """Get the most recent conversations for context injection.
        
        Returns list of dicts with 'user_text' and 'action_json'.
        """
        try:
            cursor = self._conn.execute(
                """SELECT user_text, action_json FROM conversations
                   ORDER BY id DESC LIMIT ?""",
                (limit,),
            )
            rows = cursor.fetchall()
            # Reverse to get chronological order
            return [
                {"user_text": row["user_text"], "action_json": row["action_json"]}
                for row in reversed(rows)
            ]
        except Exception as e:
            logger.error(f"Failed to get recent conversations: {e}")
            return []

    def get_conversation_count(self) -> int:
        """Get total number of stored conversations."""
        try:
            cursor = self._conn.execute("SELECT COUNT(*) FROM conversations")
            return cursor.fetchone()[0]
        except Exception:
            return 0

    def set_preference(self, key: str, value: str):
        """Set a user preference."""
        try:
            self._conn.execute(
                """INSERT INTO preferences (key, value, updated_at) 
                   VALUES (?, ?, ?)
                   ON CONFLICT(key) DO UPDATE SET value=?, updated_at=?""",
                (key, value, datetime.now().isoformat(), value, datetime.now().isoformat()),
            )
            self._conn.commit()
            logger.debug(f"Preference set: {key}={value[:50]}")
        except Exception as e:
            logger.error(f"Failed to set preference: {e}")

    def get_preference(self, key: str, default: str = None) -> Optional[str]:
        """Get a user preference."""
        try:
            cursor = self._conn.execute(
                "SELECT value FROM preferences WHERE key = ?", (key,)
            )
            row = cursor.fetchone()
            return row["value"] if row else default
        except Exception:
            return default

    def search_conversations(self, query: str, limit: int = 10) -> list[dict]:
        """Search conversations by text content."""
        try:
            cursor = self._conn.execute(
                """SELECT timestamp, user_text, action_json, result, success 
                   FROM conversations 
                   WHERE user_text LIKE ?
                   ORDER BY id DESC LIMIT ?""",
                (f"%{query}%", limit),
            )
            return [dict(row) for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Search failed: {e}")
            return []

    def clear_old_conversations(self, keep_last: int = 1000):
        """Delete old conversations, keeping the most recent ones."""
        try:
            self._conn.execute(
                """DELETE FROM conversations WHERE id NOT IN
                   (SELECT id FROM conversations ORDER BY id DESC LIMIT ?)""",
                (keep_last,),
            )
            self._conn.commit()
            logger.info(f"Cleaned old conversations (kept last {keep_last})")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")

    def close(self):
        """Close the database connection."""
        if self._conn:
            self._conn.close()
            self._conn = None
