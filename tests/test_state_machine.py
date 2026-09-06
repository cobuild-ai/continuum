"""Unit tests for Task lifecycle state machine."""
import pytest
from vibe_server.core.states import TaskState, TaskStateMachine, InvalidStateTransitionError


def test_initial_state_idle():
    sm = TaskStateMachine()
    assert sm.current_state == TaskState.IDLE


def test_valid_forward_flow():
    sm = TaskStateMachine()
    
    # IDLE -> ANALYZING_LENS
    sm.transition_to(TaskState.ANALYZING_LENS)
    assert sm.current_state == TaskState.ANALYZING_LENS
    
    # ANALYZING_LENS -> AWAITING_DESIGN_APPROVAL
    sm.transition_to(TaskState.AWAITING_DESIGN_APPROVAL)
    assert sm.current_state == TaskState.AWAITING_DESIGN_APPROVAL
    
    # AWAITING_DESIGN_APPROVAL -> SANDBOX_EXECUTING
    sm.transition_to(TaskState.SANDBOX_EXECUTING)
    assert sm.current_state == TaskState.SANDBOX_EXECUTING
    
    # SANDBOX_EXECUTING -> DIFF_READY
    sm.transition_to(TaskState.DIFF_READY)
    assert sm.current_state == TaskState.DIFF_READY
    
    # DIFF_READY -> AWAITING_MERGE_APPROVAL
    sm.transition_to(TaskState.AWAITING_MERGE_APPROVAL)
    assert sm.current_state == TaskState.AWAITING_MERGE_APPROVAL
    
    # AWAITING_MERGE_APPROVAL -> MERGED
    sm.transition_to(TaskState.MERGED)
    assert sm.current_state == TaskState.MERGED


def test_rejection_at_design_stage():
    sm = TaskStateMachine(TaskState.AWAITING_DESIGN_APPROVAL)
    sm.transition_to(TaskState.REJECTED)
    assert sm.current_state == TaskState.REJECTED


def test_rejection_at_merge_stage():
    sm = TaskStateMachine(TaskState.AWAITING_MERGE_APPROVAL)
    sm.transition_to(TaskState.REJECTED)
    assert sm.current_state == TaskState.REJECTED


def test_invalid_transition_raises():
    sm = TaskStateMachine(TaskState.IDLE)
    # Direct jump from IDLE to MERGED should fail
    with pytest.raises(InvalidStateTransitionError):
        sm.transition_to(TaskState.MERGED)


def test_failure_and_reset():
    sm = TaskStateMachine(TaskState.SANDBOX_EXECUTING)
    sm.transition_to(TaskState.FAILED)
    assert sm.current_state == TaskState.FAILED
    
    # Reset from FAILED to IDLE
    sm.transition_to(TaskState.IDLE)
    assert sm.current_state == TaskState.IDLE
