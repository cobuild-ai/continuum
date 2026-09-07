"""Chat History Manager for persisting and loading AI conversation streams per project."""
import json
import logging
import time
import uuid
from pathlib import Path
from typing import Dict, List, Optional

from vibe_server.core.models import ChatMessageItem, TaskResponse

logger = logging.getLogger(__name__)

HISTORY_STORAGE_DIR = Path.home() / ".continuum" / "chat_history"


class ChatHistoryManager:
    """Manages persistent chat conversation logs for each workspace project."""

    @classmethod
    def _get_project_key(cls, project_path: str) -> str:
        """Derive a safe filesystem key from project path."""
        p = Path(project_path).resolve()
        return p.name.lower().replace(" ", "_")

    @classmethod
    def _get_file_path(cls, project_path: str) -> Path:
        HISTORY_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
        key = cls._get_project_key(project_path)
        return HISTORY_STORAGE_DIR / f"{key}_history.json"

    @classmethod
    def get_history(cls, project_path: str) -> List[ChatMessageItem]:
        """Loads chat history for the given project. Returns default greeting if empty."""
        filepath = cls._get_file_path(project_path)
        if not filepath.exists():
            # Initial default greeting from AI
            project_name = Path(project_path).name
            default_item = ChatMessageItem(
                id=str(uuid.uuid4()),
                text=f"안녕하세요! '{project_name}' 프로젝트의 페어 프로그래머 Continuum입니다. 어떤 코드 작업이나 질문이 있으신가요?",
                isUser=False,
                timestamp=int(time.time() * 1000)
            )
            cls.save_history(project_path, [default_item])
            return [default_item]

        try:
            with open(filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
                return [ChatMessageItem(**item) for item in data]
        except Exception as e:
            logger.warning(f"Failed to load chat history from {filepath}: {e}")
            return []

    @classmethod
    def save_history(cls, project_path: str, messages: List[ChatMessageItem]) -> None:
        """Persists the conversation messages to disk."""
        filepath = cls._get_file_path(project_path)
        try:
            with open(filepath, "w", encoding="utf-8") as f:
                json.dump([item.model_dump() for item in messages], f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.error(f"Failed to save chat history to {filepath}: {e}")

    @classmethod
    def append_message(
        cls,
        project_path: str,
        text: str,
        is_user: bool,
        task: Optional[TaskResponse] = None,
        is_error: bool = False,
        error_message: Optional[str] = None
    ) -> ChatMessageItem:
        """Appends a single message to the project's chat log and saves it."""
        history = cls.get_history(project_path)
        new_item = ChatMessageItem(
            id=str(uuid.uuid4()),
            text=text,
            isUser=is_user,
            timestamp=int(time.time() * 1000),
            task=task,
            isError=is_error,
            errorMessage=error_message
        )
        history.append(new_item)
        # Limit history to latest 100 messages to prevent infinite growth
        if len(history) > 100:
            history = history[-100:]
        cls.save_history(project_path, history)
        return new_item
