from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class Database:
    def __init__(self, path: str | Path) -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def initialize(self) -> None:
        with self._connect() as connection:
            connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    token_hash TEXT NOT NULL UNIQUE,
                    mode TEXT NOT NULL DEFAULT 'pending',
                    terms_version TEXT,
                    consent_at TEXT,
                    withdrawn_at TEXT,
                    created_at TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS conversations (
                    id TEXT PRIMARY KEY,
                    session_id INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    conversation_id TEXT NOT NULL REFERENCES conversations(id) ON DELETE CASCADE,
                    role TEXT NOT NULL,
                    encrypted_content TEXT NOT NULL,
                    content_sha256 TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    model TEXT NOT NULL,
                    latency_ms REAL,
                    usage_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS research_records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    source_message_id INTEGER NOT NULL UNIQUE
                        REFERENCES messages(id) ON DELETE CASCADE,
                    role TEXT NOT NULL,
                    redacted_text TEXT NOT NULL,
                    task_class TEXT NOT NULL,
                    sensitivity_labels_json TEXT NOT NULL,
                    provider TEXT NOT NULL,
                    model TEXT NOT NULL,
                    terms_version TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER NOT NULL REFERENCES sessions(id) ON DELETE CASCADE,
                    conversation_id TEXT NOT NULL,
                    value INTEGER NOT NULL,
                    comment TEXT,
                    created_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS audit_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id INTEGER REFERENCES sessions(id) ON DELETE SET NULL,
                    event_type TEXT NOT NULL,
                    metadata_json TEXT NOT NULL,
                    created_at TEXT NOT NULL
                );

                CREATE INDEX IF NOT EXISTS idx_messages_conversation
                    ON messages(conversation_id, id);
                CREATE INDEX IF NOT EXISTS idx_research_created
                    ON research_records(created_at, id);
                """
            )

    def ensure_session(self, token_hash: str) -> dict[str, Any]:
        now = _now()
        with self._connect() as connection:
            connection.execute(
                """
                INSERT OR IGNORE INTO sessions(token_hash, created_at, updated_at)
                VALUES (?, ?, ?)
                """,
                (token_hash, now, now),
            )
            row = connection.execute(
                "SELECT * FROM sessions WHERE token_hash = ?", (token_hash,)
            ).fetchone()
        if row is None:
            raise RuntimeError("Could not create session")
        return dict(row)

    def get_session(self, token_hash: str) -> dict[str, Any] | None:
        with self._connect() as connection:
            row = connection.execute(
                "SELECT * FROM sessions WHERE token_hash = ?", (token_hash,)
            ).fetchone()
        return dict(row) if row is not None else None

    def set_consent(self, token_hash: str, mode: str, terms_version: str) -> dict[str, Any]:
        now = _now()
        with self._connect() as connection:
            connection.execute(
                """
                UPDATE sessions
                SET mode = ?, terms_version = ?, consent_at = ?, withdrawn_at = NULL,
                    updated_at = ?
                WHERE token_hash = ?
                """,
                (mode, terms_version, now, now, token_hash),
            )
            session_id = self._session_id(connection, token_hash)
            connection.execute(
                """
                INSERT INTO audit_events(session_id, event_type, metadata_json, created_at)
                VALUES (?, 'consent_updated', ?, ?)
                """,
                (session_id, json.dumps({"mode": mode, "terms_version": terms_version}), now),
            )
        session = self.get_session(token_hash)
        if session is None:
            raise RuntimeError("Session disappeared after consent update")
        return session

    def store_exchange(
        self,
        *,
        token_hash: str,
        conversation_id: str,
        user_encrypted: str,
        assistant_encrypted: str,
        user_sha256: str,
        assistant_sha256: str,
        provider: str,
        model: str,
        latency_ms: float,
        usage: dict[str, Any],
        terms_version: str,
        user_research: dict[str, Any],
        assistant_research: dict[str, Any],
    ) -> tuple[int, int]:
        now = _now()
        with self._connect() as connection:
            session_id = self._session_id(connection, token_hash)
            mode = connection.execute(
                "SELECT mode FROM sessions WHERE id = ?", (session_id,)
            ).fetchone()["mode"]
            if mode != "research":
                raise ValueError("Conversation storage is allowed only in research mode")
            connection.execute(
                """
                INSERT OR IGNORE INTO conversations(id, session_id, created_at)
                VALUES (?, ?, ?)
                """,
                (conversation_id, session_id, now),
            )
            owner = connection.execute(
                "SELECT session_id FROM conversations WHERE id = ?", (conversation_id,)
            ).fetchone()
            if owner is None or int(owner["session_id"]) != session_id:
                raise ValueError("conversation_id belongs to another session")

            user_id = self._insert_message(
                connection,
                conversation_id,
                "user",
                user_encrypted,
                user_sha256,
                provider,
                model,
                latency_ms,
                usage,
                now,
            )
            assistant_id = self._insert_message(
                connection,
                conversation_id,
                "assistant",
                assistant_encrypted,
                assistant_sha256,
                provider,
                model,
                latency_ms,
                usage,
                now,
            )
            self._insert_research(
                connection, user_id, "user", user_research, provider, model, terms_version, now
            )
            self._insert_research(
                connection,
                assistant_id,
                "assistant",
                assistant_research,
                provider,
                model,
                terms_version,
                now,
            )
            connection.execute(
                "UPDATE sessions SET updated_at = ? WHERE id = ?", (now, session_id)
            )
        return user_id, assistant_id

    def add_feedback(
        self,
        token_hash: str,
        conversation_id: str,
        value: int,
        comment: str | None,
    ) -> None:
        now = _now()
        with self._connect() as connection:
            session_id = self._session_id(connection, token_hash)
            mode = connection.execute(
                "SELECT mode FROM sessions WHERE id = ?", (session_id,)
            ).fetchone()["mode"]
            if mode != "research":
                return
            connection.execute(
                """
                INSERT INTO feedback(session_id, conversation_id, value, comment, created_at)
                VALUES (?, ?, ?, ?, ?)
                """,
                (session_id, conversation_id, value, comment, now),
            )

    def export_session_rows(self, token_hash: str) -> dict[str, Any]:
        with self._connect() as connection:
            session_id = self._session_id(connection, token_hash)
            session = connection.execute(
                "SELECT * FROM sessions WHERE id = ?", (session_id,)
            ).fetchone()
            messages = connection.execute(
                """
                SELECT m.*, c.id AS conversation_id
                FROM messages m
                JOIN conversations c ON c.id = m.conversation_id
                WHERE c.session_id = ?
                ORDER BY m.id
                """,
                (session_id,),
            ).fetchall()
        return {"session": dict(session), "messages": [dict(row) for row in messages]}

    def withdraw_and_purge(self, token_hash: str) -> None:
        now = _now()
        with self._connect() as connection:
            session_id = self._session_id(connection, token_hash)
            connection.execute("DELETE FROM conversations WHERE session_id = ?", (session_id,))
            connection.execute("DELETE FROM feedback WHERE session_id = ?", (session_id,))
            connection.execute(
                """
                UPDATE sessions
                SET mode = 'private', withdrawn_at = ?, updated_at = ?
                WHERE id = ?
                """,
                (now, now, session_id),
            )
            connection.execute(
                """
                INSERT INTO audit_events(session_id, event_type, metadata_json, created_at)
                VALUES (?, 'research_withdrawn_and_purged', '{}', ?)
                """,
                (session_id, now),
            )

    def delete_session(self, token_hash: str) -> None:
        with self._connect() as connection:
            connection.execute("DELETE FROM sessions WHERE token_hash = ?", (token_hash,))

    def admin_stats(self) -> dict[str, Any]:
        with self._connect() as connection:
            modes = connection.execute(
                "SELECT mode, COUNT(*) AS count FROM sessions GROUP BY mode"
            ).fetchall()
            counts = {
                "conversations": connection.execute(
                    "SELECT COUNT(*) AS count FROM conversations"
                ).fetchone()["count"],
                "messages": connection.execute(
                    "SELECT COUNT(*) AS count FROM messages"
                ).fetchone()["count"],
                "research_records": connection.execute(
                    "SELECT COUNT(*) AS count FROM research_records"
                ).fetchone()["count"],
                "feedback": connection.execute(
                    "SELECT COUNT(*) AS count FROM feedback"
                ).fetchone()["count"],
            }
        counts["sessions_by_mode"] = {row["mode"]: row["count"] for row in modes}
        return counts

    def research_export(self) -> list[dict[str, Any]]:
        with self._connect() as connection:
            rows = connection.execute(
                """
                SELECT id, role, redacted_text, task_class, sensitivity_labels_json,
                       provider, model, terms_version, created_at
                FROM research_records
                ORDER BY id
                """
            ).fetchall()
        result: list[dict[str, Any]] = []
        for row in rows:
            value = dict(row)
            value["sensitivity_labels"] = json.loads(value.pop("sensitivity_labels_json"))
            result.append(value)
        return result

    def _insert_message(
        self,
        connection: sqlite3.Connection,
        conversation_id: str,
        role: str,
        encrypted_content: str,
        content_sha256: str,
        provider: str,
        model: str,
        latency_ms: float,
        usage: dict[str, Any],
        created_at: str,
    ) -> int:
        cursor = connection.execute(
            """
            INSERT INTO messages(
                conversation_id, role, encrypted_content, content_sha256, provider,
                model, latency_ms, usage_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                conversation_id,
                role,
                encrypted_content,
                content_sha256,
                provider,
                model,
                latency_ms,
                json.dumps(usage, ensure_ascii=False, sort_keys=True),
                created_at,
            ),
        )
        return int(cursor.lastrowid)

    def _insert_research(
        self,
        connection: sqlite3.Connection,
        message_id: int,
        role: str,
        research: dict[str, Any],
        provider: str,
        model: str,
        terms_version: str,
        created_at: str,
    ) -> None:
        connection.execute(
            """
            INSERT INTO research_records(
                source_message_id, role, redacted_text, task_class,
                sensitivity_labels_json, provider, model, terms_version, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                message_id,
                role,
                research["text"],
                research["task_class"],
                json.dumps(research["labels"], ensure_ascii=False, sort_keys=True),
                provider,
                model,
                terms_version,
                created_at,
            ),
        )

    def _session_id(self, connection: sqlite3.Connection, token_hash: str) -> int:
        row = connection.execute(
            "SELECT id FROM sessions WHERE token_hash = ?", (token_hash,)
        ).fetchone()
        if row is None:
            raise KeyError("Unknown session")
        return int(row["id"])

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path, timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA foreign_keys = ON")
        connection.execute("PRAGMA journal_mode = WAL")
        connection.execute("PRAGMA busy_timeout = 5000")
        return connection


def _now() -> str:
    return datetime.now(UTC).isoformat()
