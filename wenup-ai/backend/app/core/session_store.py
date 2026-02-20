from __future__ import annotations

import sqlite3
import threading
from datetime import datetime, timedelta
from typing import Optional

from app.models.session import Session


class SessionStore:
    """
    SQLite-backed session store. Thread-safe via a module-level lock.

    Stores each session as a JSON blob keyed by session_id.
    Replace with Redis or Postgres by swapping this class — the interface is stable.
    """

    def __init__(self, db_path: str = "sessions.db") -> None:
        self._lock = threading.Lock()
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._init_schema()

    def _init_schema(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS sessions (
                session_id      TEXT PRIMARY KEY,
                data            TEXT NOT NULL,
                last_activity   TEXT NOT NULL
            )
            """
        )
        self._conn.commit()

    # ------------------------------------------------------------------
    # CRUD
    # ------------------------------------------------------------------

    def get(self, session_id: str) -> Optional[Session]:
        with self._lock:
            cursor = self._conn.execute(
                "SELECT data FROM sessions WHERE session_id = ?",
                (session_id,),
            )
            row = cursor.fetchone()
        if row is None:
            return None
        return Session.model_validate_json(row[0])

    def save(self, session: Session) -> None:
        session.last_activity_at = datetime.utcnow()
        with self._lock:
            self._conn.execute(
                """
                INSERT INTO sessions (session_id, data, last_activity)
                VALUES (?, ?, ?)
                ON CONFLICT(session_id) DO UPDATE SET
                    data = excluded.data,
                    last_activity = excluded.last_activity
                """,
                (
                    session.session_id,
                    session.model_dump_json(),
                    session.last_activity_at.isoformat(),
                ),
            )
            self._conn.commit()

    def delete(self, session_id: str) -> None:
        with self._lock:
            self._conn.execute(
                "DELETE FROM sessions WHERE session_id = ?",
                (session_id,),
            )
            self._conn.commit()

    def purge_expired(self, ttl_seconds: int = 3600) -> int:
        """Delete sessions inactive for longer than ttl_seconds. Returns count deleted."""
        cutoff = (datetime.utcnow() - timedelta(seconds=ttl_seconds)).isoformat()
        with self._lock:
            cursor = self._conn.execute(
                "DELETE FROM sessions WHERE last_activity < ?",
                (cutoff,),
            )
            self._conn.commit()
            return cursor.rowcount


# ---------------------------------------------------------------------------
# FastAPI dependency — single instance shared across requests
# ---------------------------------------------------------------------------

_store: Optional[SessionStore] = None


def get_session_store() -> SessionStore:
    global _store
    if _store is None:
        _store = SessionStore()
    return _store
