"""Tests for SQLite ChatHistoryManager and Auto-Retention Policy."""
import os
import tempfile
import time
from pathlib import Path
import pytest

from vibe_server.core.chat_history_manager import ChatHistoryManager
from vibe_server.core.config import settings


@pytest.fixture
def temp_chat_db(monkeypatch):
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_db = Path(tmpdir) / "test_chat.db"
        monkeypatch.setattr(settings, "chat_db_path", tmp_db)
        monkeypatch.setattr(settings, "chat_retention_days", 90)
        yield tmp_db


def test_sqlite_append_and_get_history(temp_chat_db):
    project = "/tmp/test_project"
    
    # 1. First read should initialize DB and return initial greeting
    history = ChatHistoryManager.get_history(project)
    assert len(history) == 1
    assert not history[0].isUser
    assert "test_project" in history[0].text

    # 2. Append user message
    user_msg = ChatHistoryManager.append_message(project, "Hello Continuum", is_user=True)
    assert user_msg.isUser
    assert user_msg.text == "Hello Continuum"

    # 3. Append assistant message
    ai_msg = ChatHistoryManager.append_message(project, "I am ready to help", is_user=False)
    assert not ai_msg.isUser

    # 4. Check history retrieval
    updated_history = ChatHistoryManager.get_history(project)
    assert len(updated_history) == 3
    assert updated_history[1].text == "Hello Continuum"
    assert updated_history[2].text == "I am ready to help"


def test_retention_policy_purge(temp_chat_db, monkeypatch):
    project = "/tmp/test_purge_project"
    
    # Create an old message manually with timestamp 100 days ago
    ChatHistoryManager._init_db()
    old_ts = int((time.time() - (100 * 86400)) * 1000)
    
    import sqlite3
    with sqlite3.connect(temp_chat_db) as conn:
        conn.execute(
            "INSERT INTO chat_messages (id, project_path, text, is_user, timestamp) VALUES (?, ?, ?, ?, ?)",
            ("old-msg-id", str(Path(project).resolve()), "Old message from 100 days ago", 1, old_ts)
        )
        conn.commit()

    # Create a fresh message
    fresh_msg = ChatHistoryManager.append_message(project, "Fresh message from today", is_user=True)

    # Purge with retention_days = 90
    deleted_count = ChatHistoryManager.purge_expired_messages(retention_days=90)
    assert deleted_count >= 1

    # Verify that only fresh message remains
    history = ChatHistoryManager.get_history(project)
    texts = [m.text for m in history]
    assert "Old message from 100 days ago" not in texts
    assert "Fresh message from today" in texts
