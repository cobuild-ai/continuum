"""Pydantic data models and schemas for Continuum — synchronized with SkyBrain 5-Lens."""
from datetime import datetime, timezone
import enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field
from vibe_server.core.states import TaskState


class Severity(str, enum.Enum):
    """Finding severity levels, ordered by criticality."""
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"
    INFO = "INFO"


class LensCategory(str, enum.Enum):
    """Review lens category identifiers (100% aligned with SkyBrain)."""
    CLEAN_CODE = "clean_code"
    CLEAN_ARCHITECTURE = "clean_architecture"
    SECURITY = "security"
    PERFORMANCE = "performance"
    AI_CONDUCT = "ai_conduct"


class FindingItem(BaseModel):
    """A single actionable code review finding."""
    category: LensCategory
    severity: Severity = Severity.MEDIUM
    principle_violated: str
    description: str
    suggestion: str
    file: Optional[str] = None
    line: Optional[int] = None


class LensEvaluation(BaseModel):
    """Result of an individual lens evaluation."""
    category: LensCategory
    lens_name: str
    passed: bool
    score: int = Field(ge=0, le=100, description="Score out of 100")
    findings: List[FindingItem] = Field(default_factory=list)
    recommendations: List[str] = Field(default_factory=list)


class LensReport(BaseModel):
    """Comprehensive 5-Lens analysis report (SkyBrain aligned)."""
    overall_passed: bool
    average_score: float
    evaluations: Dict[str, LensEvaluation] = Field(default_factory=dict)
    summary: str = ""


class FileDiff(BaseModel):
    """Diff details for a single file."""
    filepath: str
    additions: int = 0
    deletions: int = 0
    patch: str = ""


class DiffSummary(BaseModel):
    """Summary of all changes produced by the task."""
    total_files_changed: int = 0
    total_additions: int = 0
    total_deletions: int = 0
    files: List[FileDiff] = Field(default_factory=list)


class TaskCreateRequest(BaseModel):
    """Request schema to create a new vibe task."""
    prompt: str = Field(..., min_length=3, description="User instruction or goal")
    target_repo_path: Optional[str] = None
    base_branch: str = "main"


class ApprovalRequest(BaseModel):
    """User approval response from mobile."""
    approved: bool
    feedback: Optional[str] = None


class FCMPayload(BaseModel):
    """FCM Push Notification payload for Android client."""
    task_id: str
    state: TaskState
    title: str
    body: str
    files_changed_count: int = 0
    requires_user_action: bool = False
    action_type: Optional[str] = None  # DESIGN_APPROVAL, MERGE_APPROVAL, VIEW_ERROR


class VerificationReport(BaseModel):
    """Execution and test verification metrics for the task."""
    verified: bool = False
    tests_passed: bool = False
    total_tests: int = 0
    passed_tests: int = 0
    failed_tests: int = 0
    execution_time_seconds: float = 0.0
    command_run: str = ""
    summary: str = ""
    iterations: int = 1
    raw_output: str = ""


class TaskResponse(BaseModel):
    """Complete task response object."""
    id: str
    prompt: str
    state: TaskState
    branch_name: str
    lens_report: Optional[LensReport] = None
    diff_summary: Optional[DiffSummary] = None
    verification_report: Optional[VerificationReport] = None
    error_message: Optional[str] = None
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))


class ProjectInfo(BaseModel):
    """Discovered or active target managed project info."""
    name: str
    path: str
    current_branch: str = "main"
    is_git: bool = True
    is_clean: bool = True
    description: str = ""


class ProjectSelectRequest(BaseModel):
    """Request to set the active managed project."""
    path: str


class ProjectCreateRequest(BaseModel):
    """Request to create and provision a new managed project."""
    name: str
    parent_path: Optional[str] = None
    tech_stack: Optional[str] = "python"  # python, android, node, default


class ChatRequest(BaseModel):
    """Conversational Vibe Coding input request."""
    message: str
    target_repo_path: Optional[str] = None
    conversation_history: List[Dict[str, str]] = Field(default_factory=list)


class ChatResponse(BaseModel):
    """Conversational Vibe Coding output response."""
    reply: str
    is_task: bool = False
    task: Optional[TaskResponse] = None


class ChatMessageItem(BaseModel):
    """Represents a persisted chat conversation message for mobile IDE synchronization."""
    id: str
    text: str
    isUser: bool
    timestamp: int
    task: Optional[TaskResponse] = None
    isError: bool = False
    errorMessage: Optional[str] = None

