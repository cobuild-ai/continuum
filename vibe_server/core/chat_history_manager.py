"""SQLite-backed Chat History Manager with auto-expiration (retention policy)."""
import json
import logging
import sqlite3
import time
import uuid
from pathlib import Path
from typing import List, Optional

from vibe_server.core.config import settings
from vibe_server.core.models import ChatMessageItem, TaskResponse

logger = logging.getLogger(__name__)


class ChatHistoryManager:
    """
    Manages persistent chat conversation logs for each workspace project
    using an embedded SQLite database with automatic retention cleanup.
    """

    @classmethod
    def _get_db_path(cls) -> Path:
        db_path = settings.chat_db_path
        db_path.parent.mkdir(parents=True, exist_ok=True)
        return db_path

    @classmethod
    def _init_db(cls) -> None:
        """Initializes table schema and indices if not present."""
        db_path = cls._get_db_path()
        with sqlite3.connect(db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS chat_messages (
                    id TEXT PRIMARY KEY,
                    project_path TEXT NOT NULL,
                    text TEXT NOT NULL,
                    is_user INTEGER NOT NULL,
                    timestamp INTEGER NOT NULL,
                    task_json TEXT,
                    is_error INTEGER DEFAULT 0,
                    error_message TEXT,
                    engine TEXT
                );
            """)
            # Auto-migrate existing databases to add engine column if missing
            try:
                conn.execute("ALTER TABLE chat_messages ADD COLUMN engine TEXT;")
            except sqlite3.OperationalError:
                pass

            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_chat_project_ts
                ON chat_messages(project_path, timestamp ASC);
            """)
            conn.commit()

    @classmethod
    def purge_expired_messages(cls, retention_days: Optional[int] = None) -> int:
        """
        Deletes messages older than the retention threshold.
        If retention_days is 0, retention is disabled (records kept indefinitely).
        Returns the number of deleted rows.
        """
        days = retention_days if retention_days is not None else settings.chat_retention_days
        if days <= 0:
            return 0

        cutoff_ms = int((time.time() - (days * 86400)) * 1000)
        cls._init_db()
        db_path = cls._get_db_path()
        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.execute(
                    "DELETE FROM chat_messages WHERE timestamp < ?",
                    (cutoff_ms,)
                )
                deleted = cursor.rowcount
                conn.commit()
                if deleted > 0:
                    logger.info(f"Purged {deleted} chat messages older than {days} days (cutoff: {cutoff_ms}).")
                return deleted
        except Exception as e:
            logger.error(f"Failed to purge expired chat messages: {e}")
            return 0

    @classmethod
    def get_history(cls, project_path: str, limit: int = 100) -> List[ChatMessageItem]:
        """Loads chat history for the given project from SQLite. Returns default greeting if empty."""
        cls._init_db()
        # Auto-purge expired messages on read
        cls.purge_expired_messages()

        db_path = cls._get_db_path()
        resolved_path = str(Path(project_path).resolve())

        try:
            with sqlite3.connect(db_path) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.execute(
                    """
                    SELECT id, text, is_user, timestamp, task_json, is_error, error_message, engine
                    FROM chat_messages
                    WHERE project_path = ?
                    ORDER BY timestamp ASC
                    LIMIT ?
                    """,
                    (resolved_path, limit)
                )
                rows = cursor.fetchall()
                if rows:
                    messages = []
                    for row in rows:
                        task_obj = None
                        if row["task_json"]:
                            try:
                                task_obj = TaskResponse(**json.loads(row["task_json"]))
                            except Exception:
                                pass

                        messages.append(ChatMessageItem(
                            id=row["id"],
                            text=row["text"],
                            isUser=bool(row["is_user"]),
                            timestamp=row["timestamp"],
                            task=task_obj,
                            isError=bool(row["is_error"]),
                            errorMessage=row["error_message"],
                            engine=row["engine"] if "engine" in row.keys() else None
                        ))
                    return messages
        except Exception as e:
            logger.warning(f"Failed to load chat history from SQLite: {e}")

        # If empty, create initial default greeting from AI
        project_name = Path(project_path).name
        default_greeting = (
            f"안녕하세요! '{project_name}' 프로젝트의 페어 프로그래머 Continuum입니다. "
            f"어떤 코드 작업이나 아키텍처 질문이 있으신가요?"
        )
        default_item = cls.append_message(
            project_path=resolved_path,
            text=default_greeting,
            is_user=False,
            engine="Continuum AI"
        )
        return [default_item]

    @classmethod
    def append_message(
        cls,
        project_path: str,
        text: str,
        is_user: bool,
        task: Optional[TaskResponse] = None,
        is_error: bool = False,
        error_message: Optional[str] = None,
        engine: Optional[str] = None
    ) -> ChatMessageItem:
        """Appends a single message to SQLite and returns the constructed item."""
        cls._init_db()
        db_path = cls._get_db_path()
        resolved_path = str(Path(project_path).resolve())

        msg_id = str(uuid.uuid4())
        ts = int(time.time() * 1000)
        task_json_str = json.dumps(task.model_dump(mode="json")) if task else None
        sender_engine = "user" if is_user else (engine or "Continuum AI")

        try:
            with sqlite3.connect(db_path) as conn:
                conn.execute(
                    """
                    INSERT INTO chat_messages (id, project_path, text, is_user, timestamp, task_json, is_error, error_message, engine)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (
                        msg_id,
                        resolved_path,
                        text,
                        1 if is_user else 0,
                        ts,
                        task_json_str,
                        1 if is_error else 0,
                        error_message,
                        sender_engine
                    )
                )
                conn.commit()
        except Exception as e:
            logger.error(f"Failed to insert chat message into SQLite: {e}")

        return ChatMessageItem(
            id=msg_id,
            text=text,
            isUser=is_user,
            timestamp=ts,
            task=task,
            isError=is_error,
            errorMessage=error_message,
            engine=sender_engine
        )

    @classmethod
    def clear_history(cls, project_path: str) -> int:
        """Explicitly deletes all conversation messages for a project to start a clean new session."""
        cls._init_db()
        db_path = cls._get_db_path()
        resolved_path = str(Path(project_path).resolve())

        try:
            with sqlite3.connect(db_path) as conn:
                cursor = conn.execute(
                    "DELETE FROM chat_messages WHERE project_path = ?",
                    (resolved_path,)
                )
                deleted = cursor.rowcount
                conn.commit()
                logger.info(f"Cleared {deleted} chat messages for project: {resolved_path}")
                return deleted
        except Exception as e:
            logger.error(f"Failed to clear chat history for {resolved_path}: {e}")
            return 0
