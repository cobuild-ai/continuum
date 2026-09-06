"""Task lifecycle states and state machine transitions."""
from enum import Enum
from typing import Dict, Set


class TaskState(str, Enum):
    IDLE = "IDLE"
    ANALYZING_LENS = "ANALYZING_LENS"
    AWAITING_DESIGN_APPROVAL = "AWAITING_DESIGN_APPROVAL"
    SANDBOX_EXECUTING = "SANDBOX_EXECUTING"
    DIFF_READY = "DIFF_READY"
    AWAITING_MERGE_APPROVAL = "AWAITING_MERGE_APPROVAL"
    MERGED = "MERGED"
    REJECTED = "REJECTED"
    FAILED = "FAILED"


# Valid state transitions
VALID_TRANSITIONS: Dict[TaskState, Set[TaskState]] = {
    TaskState.IDLE: {TaskState.ANALYZING_LENS, TaskState.FAILED},
    TaskState.ANALYZING_LENS: {TaskState.AWAITING_DESIGN_APPROVAL, TaskState.FAILED},
    TaskState.AWAITING_DESIGN_APPROVAL: {TaskState.SANDBOX_EXECUTING, TaskState.REJECTED, TaskState.FAILED},
    TaskState.SANDBOX_EXECUTING: {TaskState.DIFF_READY, TaskState.FAILED},
    TaskState.DIFF_READY: {TaskState.AWAITING_MERGE_APPROVAL, TaskState.FAILED},
    TaskState.AWAITING_MERGE_APPROVAL: {TaskState.MERGED, TaskState.REJECTED, TaskState.FAILED},
    TaskState.MERGED: set(),
    TaskState.REJECTED: set(),
    TaskState.FAILED: {TaskState.IDLE}  # Can reset
}


class InvalidStateTransitionError(Exception):
    """Raised when an invalid state transition is attempted."""
    pass


class TaskStateMachine:
    """Manages the state transitions of an active Vibe task."""

    def __init__(self, initial_state: TaskState = TaskState.IDLE):
        self._current_state = initial_state

    @property
    def current_state(self) -> TaskState:
        return self._current_state

    def can_transition_to(self, new_state: TaskState) -> bool:
        allowed = VALID_TRANSITIONS.get(self._current_state, set())
        return new_state in allowed

    def transition_to(self, new_state: TaskState) -> TaskState:
        if not self.can_transition_to(new_state):
            raise InvalidStateTransitionError(
                f"Cannot transition from {self._current_state} to {new_state}"
            )
        self._current_state = new_state
        return self._current_state
