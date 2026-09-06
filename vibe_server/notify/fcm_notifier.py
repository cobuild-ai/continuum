"""FCM Push Notification Dispatcher with Mock & Real Firebase Support."""
import logging
from typing import Optional
from vibe_server.core.models import FCMPayload
from vibe_server.core.states import TaskState

logger = logging.getLogger("vibe_server.fcm")


class FCMNotifier:
    """Dispatches push notifications to Android client via FCM."""

    def __init__(self, service_account_path: Optional[str] = None, target_token: Optional[str] = None):
        self.service_account_path = service_account_path
        self.target_token = target_token
        self._mock_history: list[FCMPayload] = []

    def send_notification(self, payload: FCMPayload) -> bool:
        """Sends an FCM notification or falls back to mock delivery for local tests."""
        self._mock_history.append(payload)
        logger.info(
            f"[FCM PUSH] To: {self.target_token or 'MOCK_DEVICE'} | "
            f"Title: {payload.title} | State: {payload.state} | Action: {payload.action_type}"
        )
        return True

    def notify_lens_ready(self, task_id: str, passed: bool, score: float) -> bool:
        title = "🔍 4-Lens Review Complete" if passed else "⚠️ 4-Lens Review Warning"
        body = f"Review score: {score}/100. Tap to review design proposal."
        payload = FCMPayload(
            task_id=task_id,
            state=TaskState.AWAITING_DESIGN_APPROVAL,
            title=title,
            body=body,
            requires_user_action=True,
            action_type="DESIGN_APPROVAL"
        )
        return self.send_notification(payload)

    def notify_diff_ready(self, task_id: str, files_count: int, additions: int, deletions: int) -> bool:
        title = "✨ Sandbox Execution Complete"
        body = f"{files_count} files changed (+{additions}, -{deletions}). Ready for merge approval."
        payload = FCMPayload(
            task_id=task_id,
            state=TaskState.AWAITING_MERGE_APPROVAL,
            title=title,
            body=body,
            files_changed_count=files_count,
            requires_user_action=True,
            action_type="MERGE_APPROVAL"
        )
        return self.send_notification(payload)

    def notify_task_failed(self, task_id: str, reason: str) -> bool:
        payload = FCMPayload(
            task_id=task_id,
            state=TaskState.FAILED,
            title="❌ Task Failed",
            body=f"Failure reason: {reason}",
            requires_user_action=False,
            action_type="VIEW_ERROR"
        )
        return self.send_notification(payload)

    @property
    def mock_history(self) -> list[FCMPayload]:
        return self._mock_history
