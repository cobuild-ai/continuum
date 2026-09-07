"""Continuum Vibe Server: FastAPI Web Application & Typer CLI entrypoint."""
import asyncio
import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
import subprocess
from typing import Dict, List, Optional

import typer
import uvicorn
from fastapi import FastAPI, HTTPException, status
from fastapi.responses import StreamingResponse
from rich.console import Console
from rich.table import Table

from vibe_server.core.ai_client import SkyBrainCircuitBreaker
from vibe_server.core.config import settings
from vibe_server.core.conversational_agent import ConversationalAgent
from vibe_server.core.diagnostics import CheckStatus, PreflightAssessor
from vibe_server.core.models import (
    ApprovalRequest,
    ChatRequest,
    ChatResponse,
    DiffSummary,
    ProjectCreateRequest,
    ProjectInfo,
    ProjectSelectRequest,
    TaskCreateRequest,
    TaskResponse,
)
from vibe_server.core.project_provisioner import ProjectProvisioner
from vibe_server.core.states import TaskState, TaskStateMachine
from vibe_server.lens.engine import FiveLensEngine
from vibe_server.notify.fcm_notifier import FCMNotifier
from vibe_server.sandbox.git_workspace import GitWorkspaceManager
from vibe_server.sandbox.synthesizer import CodeSynthesizer

console = Console()
app = FastAPI(
    title="Continuum Vibe Server",
    version="0.1.0",
    description="Mobile-First Vibe Coding & Host Sandbox Orchestrator API"
)

# In-memory Task Repository for Orchestrator
tasks_db: Dict[str, dict] = {}
notifier = FCMNotifier()
lens_engine = FiveLensEngine()
code_synth = CodeSynthesizer()
conv_agent = ConversationalAgent()


@app.get("/health", tags=["System"])
def health_check():
    return {
        "status": "healthy",
        "service": settings.app_name,
        "ai_engine": {
            "provider": settings.ai_provider,
            "model": settings.active_model_name,
            "custom_gateway": bool(settings.custom_api_url),
            "skybrain_enabled": settings.skybrain_enabled,
            "skybrain_online": SkyBrainCircuitBreaker.is_alive(settings.skybrain_url) if settings.skybrain_enabled else False,
            "skybrain_model": settings.skybrain_model if settings.skybrain_enabled else None
        },
        "timestamp": datetime.now(timezone.utc).isoformat()
    }


@app.get("/health/diagnostics", tags=["System"])
def diagnostics_check():
    assessor = PreflightAssessor(target_port=settings.port, workspace_root=settings.default_workspace_root)
    report = assessor.run_all_checks()
    return {
        "allowed": report.allowed,
        "summary": report.summary,
        "has_warnings": report.has_warnings,
        "has_failures": report.has_failures,
        "checks": [
            {
                "name": c.name,
                "status": c.status.value,
                "message": c.message,
                "resolution": c.resolution
            }
            for c in report.checks
        ]
    }


active_project_path: str = str(settings.default_workspace_root / "deartalk-ai")


def _extract_project_description(project_dir: Path) -> str:
    """Dynamically extracts a description from README.md or pyproject.toml without hardcoding."""
    readme = project_dir / "README.md"
    if readme.exists():
        try:
            lines = readme.read_text(encoding="utf-8").splitlines()
            for line in lines:
                clean = line.strip().lstrip("#").strip()
                if clean and not clean.startswith(("[", "!", "<", "---")):
                    return clean[:80]
        except Exception:
            pass
    pyproject = project_dir / "pyproject.toml"
    if pyproject.exists():
        try:
            content = pyproject.read_text(encoding="utf-8")
            match = re.search(r'description\s*=\s*["\']([^"\']+)["\']', content)
            if match:
                return match.group(1).strip()[:80]
        except Exception:
            pass
    return "Managed Workspace Project"


def discover_projects(workspace_root: Path) -> List[ProjectInfo]:
    """Scan and return all production projects under workspace."""
    projects: List[ProjectInfo] = []
    scan_dir = workspace_root / "01-production" if (workspace_root / "01-production").exists() else workspace_root
    if not scan_dir.exists():
        return projects

    for item in sorted(scan_dir.iterdir()):
        if item.is_dir() and not item.name.startswith((".", "__")):
            is_git = (item / ".git").exists()
            branch = "main"
            is_clean = True
            if is_git:
                try:
                    res = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=item, capture_output=True, text=True)
                    if res.returncode == 0 and res.stdout.strip():
                        branch = res.stdout.strip()
                    status_res = subprocess.run(["git", "status", "--porcelain"], cwd=item, capture_output=True, text=True)
                    if status_res.returncode == 0:
                        is_clean = len(status_res.stdout.strip()) == 0
                except Exception:
                    pass

            desc = _extract_project_description(item)

            projects.append(ProjectInfo(
                name=item.name,
                path=str(item.resolve()),
                current_branch=branch,
                is_git=is_git,
                is_clean=is_clean,
                description=desc
            ))
    return projects


@app.get("/api/v1/projects", response_model=List[ProjectInfo], tags=["Projects"])
def list_projects():
    """List discovered projects available for management."""
    return discover_projects(settings.default_workspace_root)


@app.get("/api/v1/projects/active", response_model=ProjectInfo, tags=["Projects"])
def get_active_project():
    """Get the currently opened/active target managed project."""
    global active_project_path
    p = Path(active_project_path)
    if not p.exists():
        active_project_path = str(settings.default_workspace_root / "deartalk-ai")
        p = Path(active_project_path)

    is_git = (p / ".git").exists()
    branch = "main"
    is_clean = True
    if is_git:
        try:
            res = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=p, capture_output=True, text=True)
            if res.returncode == 0 and res.stdout.strip():
                branch = res.stdout.strip()
            status_res = subprocess.run(["git", "status", "--porcelain"], cwd=p, capture_output=True, text=True)
            if status_res.returncode == 0:
                is_clean = len(status_res.stdout.strip()) == 0
        except Exception:
            pass

    return ProjectInfo(
        name=p.name,
        path=str(p.resolve()),
        current_branch=branch,
        is_git=is_git,
        is_clean=is_clean,
        description="Active Target Project"
    )


@app.post("/api/v1/projects/select", response_model=ProjectInfo, tags=["Projects"])
def select_project(req: ProjectSelectRequest):
    """Set the active managed project path and ensure it is properly Git provisioned."""
    global active_project_path
    raw_path = Path(req.path)
    if not raw_path.is_absolute():
        p = (settings.default_workspace_root / req.path).resolve()
    else:
        p = raw_path.resolve()

    if not p.exists() or not p.is_dir():
        raise HTTPException(status_code=400, detail=f"Invalid project path: {req.path}")
    
    # Ensure Git sovereignty and .gitignore
    ProjectProvisioner.ensure_git_repository(p)
    active_project_path = str(p.resolve())
    return get_active_project()


@app.post("/api/v1/projects/create", response_model=ProjectInfo, tags=["Projects"])
def create_project(req: ProjectCreateRequest):
    """
    Creates and provisions a new project under 01-production with automatic Git and tailored .gitignore.
    Binds the newly created project as the single active managed project.
    """
    global active_project_path
    parent = Path(req.parent_path).resolve() if req.parent_path else settings.default_workspace_root
    new_dir = (parent / req.name).resolve()
    new_dir.mkdir(parents=True, exist_ok=True)
    
    # Ensure Git & tailored .gitignore
    ProjectProvisioner.ensure_git_repository(new_dir)
    active_project_path = str(new_dir.resolve())
    return get_active_project()


@app.post("/api/v1/chat", response_model=ChatResponse, tags=["Chat"])
def chat_with_agent(req: ChatRequest):
    """
    Conversational Vibe Coding endpoint (Antigravity-style mobile pair programming).
    - If inquiry / question / discussion: returns AI markdown reply directly.
    - If on-demand 5-Lens audit requested: runs real project 5-Lens static analysis.
    - If actionable code task: directly creates task branch, executes in sandbox, verifies with real tests, and presents diff for merge approval.
    """
    target_path = Path(req.target_repo_path or active_project_path)
    
    # 1. On-Demand 5-Lens Diagnostic: ONLY when explicitly requested by user
    if conv_agent.is_lens_audit_intent(req.message):
        task_id = str(uuid.uuid4())[:8]
        report = lens_engine.evaluate_project(target_path)
        task_res = TaskResponse(
            id=task_id,
            prompt=req.message,
            state=TaskState.AWAITING_DESIGN_APPROVAL,
            branch_name=f"{settings.ai_branch_prefix}{task_id}",
            lens_report=report,
            diff_summary=None,
            verification_report=None,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc)
        )
        task_data = {
            "id": task_id,
            "prompt": req.message,
            "state_machine": TaskStateMachine(TaskState.AWAITING_DESIGN_APPROVAL),
            "state": TaskState.AWAITING_DESIGN_APPROVAL,
            "branch_name": f"{settings.ai_branch_prefix}{task_id}",
            "lens_report": report,
            "diff_summary": None,
            "verification_report": None,
            "error_message": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "target_repo_path": str(target_path),
            "base_branch": "main"
        }
        tasks_db[task_id] = task_data
        return ChatResponse(
            reply=f"🔍 **[{target_path.name}]** 요청하신 5대 렌즈 실시간 정적 분석을 완료했습니다. (종합 점수: {report.average_score}점)",
            is_task=True,
            task=task_res
        )

    # 2. Actionable Code Task -> Direct execution, test verification & Diff presentation!
    elif conv_agent.is_code_task_intent(req.message):
        task_id = str(uuid.uuid4())[:8]
        sm = TaskStateMachine(TaskState.SANDBOX_EXECUTING)
        branch_name = f"{settings.ai_branch_prefix}{task_id}"
        has_git = (target_path / ".git").exists()
        
        if not has_git:
            ProjectProvisioner.ensure_git_repository(target_path)
            
        git_mgr = GitWorkspaceManager(target_path, branch_prefix=settings.ai_branch_prefix)
        git_mgr.create_task_branch(task_id, base_branch="main")
        modified_files, ver_report = code_synth.execute_and_verify(target_path, req.message, task_id)
        diff_summary = git_mgr.get_diff(task_id, base_branch="main")
        
        sm.transition_to(TaskState.DIFF_READY)
        sm.transition_to(TaskState.AWAITING_MERGE_APPROVAL)
        
        task_data = {
            "id": task_id,
            "prompt": req.message,
            "state_machine": sm,
            "state": sm.current_state,
            "branch_name": branch_name,
            "lens_report": None,  # No unsolicited lens card!
            "diff_summary": diff_summary,
            "verification_report": ver_report,
            "error_message": None,
            "created_at": datetime.now(timezone.utc),
            "updated_at": datetime.now(timezone.utc),
            "target_repo_path": str(target_path),
            "base_branch": "main"
        }
        tasks_db[task_id] = task_data
        
        notifier.notify_diff_ready(
            task_id,
            diff_summary.total_files_changed,
            diff_summary.total_additions,
            diff_summary.total_deletions
        )
        
        return ChatResponse(
            reply=f"🛠️ **[{target_path.name}]** 코드 구현 및 실측 테스트 검증이 완료되었습니다. 변경사항(Diff)을 검토 후 승인(Squash Merge)해주세요.",
            is_task=True,
            task=TaskResponse(
                id=task_id,
                prompt=req.message,
                state=sm.current_state,
                branch_name=branch_name,
                lens_report=None,
                diff_summary=diff_summary,
                verification_report=ver_report,
                created_at=task_data["created_at"],
                updated_at=task_data["updated_at"]
            )
        )
    else:
        # Conversational Q&A / architecture dialog
        reply_text = conv_agent.chat(target_path, req.message, req.conversation_history)
        return ChatResponse(
            reply=reply_text,
            is_task=False,
            task=None
        )


@app.post("/api/v1/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED, tags=["Tasks"])
def create_task(req: TaskCreateRequest):
    task_id = str(uuid.uuid4())[:8]
    sm = TaskStateMachine(TaskState.IDLE)
    
    # 1. State: ANALYZING_LENS
    sm.transition_to(TaskState.ANALYZING_LENS)
    report = lens_engine.evaluate(req.prompt)
    
    # 2. State: AWAITING_DESIGN_APPROVAL
    sm.transition_to(TaskState.AWAITING_DESIGN_APPROVAL)
    
    branch_name = f"{settings.ai_branch_prefix}{task_id}"
    target_repo = req.target_repo_path or active_project_path
    task_data = {
        "id": task_id,
        "prompt": req.prompt,
        "state_machine": sm,
        "state": sm.current_state,
        "branch_name": branch_name,
        "lens_report": report,
        "diff_summary": None,
        "verification_report": None,
        "error_message": None,
        "created_at": datetime.now(timezone.utc),
        "updated_at": datetime.now(timezone.utc),
        "target_repo_path": target_repo,
        "base_branch": req.base_branch
    }
    tasks_db[task_id] = task_data
    
    # Send FCM notification to mobile
    notifier.notify_lens_ready(task_id, report.overall_passed, report.average_score)
    
    return TaskResponse(
        id=task_id,
        prompt=req.prompt,
        state=sm.current_state,
        branch_name=branch_name,
        lens_report=report,
        verification_report=None,
        created_at=task_data["created_at"],
        updated_at=task_data["updated_at"]
    )


@app.get("/api/v1/tasks/{task_id}", response_model=TaskResponse, tags=["Tasks"])
def get_task(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    t = tasks_db[task_id]
    return TaskResponse(
        id=t["id"],
        prompt=t["prompt"],
        state=t["state_machine"].current_state,
        branch_name=t["branch_name"],
        lens_report=t["lens_report"],
        diff_summary=t["diff_summary"],
        verification_report=t.get("verification_report"),
        error_message=t["error_message"],
        created_at=t["created_at"],
        updated_at=t["updated_at"]
    )


@app.post("/api/v1/tasks/{task_id}/approve", response_model=TaskResponse, tags=["Tasks"])
def approve_task_stage(task_id: str, req: ApprovalRequest):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    
    t = tasks_db[task_id]
    sm: TaskStateMachine = t["state_machine"]
    
    target_path = Path(t["target_repo_path"])
    has_git = (target_path / ".git").exists()

    if not req.approved:
        if has_git:
            git_mgr = GitWorkspaceManager(target_path, branch_prefix=settings.ai_branch_prefix)
            try:
                git_mgr.discard_task_branch(task_id, base_branch=t["base_branch"])
            except Exception:
                pass
        sm.transition_to(TaskState.REJECTED)
        t["state"] = sm.current_state
        t["updated_at"] = datetime.now(timezone.utc)
        return get_task(task_id)

    # If at AWAITING_DESIGN_APPROVAL -> proceed to execution
    if sm.current_state == TaskState.AWAITING_DESIGN_APPROVAL:
        sm.transition_to(TaskState.SANDBOX_EXECUTING)
        
        if not has_git:
            t["error_message"] = f"Target path is not a valid Git repository: {target_path}"
            sm.transition_to(TaskState.FAILED)
            t["state"] = sm.current_state
            t["updated_at"] = datetime.now(timezone.utc)
            return get_task(task_id)

        git_mgr = GitWorkspaceManager(target_path, branch_prefix=settings.ai_branch_prefix)
        try:
            git_mgr.create_task_branch(task_id, base_branch=t["base_branch"])
            _, ver_report = code_synth.execute_and_verify(target_path, t["prompt"], task_id)
            t["verification_report"] = ver_report
            t["diff_summary"] = git_mgr.get_diff(task_id, base_branch=t["base_branch"])
            sm.transition_to(TaskState.DIFF_READY)
            sm.transition_to(TaskState.AWAITING_MERGE_APPROVAL)
            
            diff_summary = t["diff_summary"]
            notifier.notify_diff_ready(
                task_id,
                diff_summary.total_files_changed,
                diff_summary.total_additions,
                diff_summary.total_deletions
            )
        except Exception as e:
            t["error_message"] = f"Task execution failed: {e}"
            sm.transition_to(TaskState.FAILED)

    # If at AWAITING_MERGE_APPROVAL -> finalize squash merge
    elif sm.current_state == TaskState.AWAITING_MERGE_APPROVAL:
        if not has_git:
            t["error_message"] = f"Target path is not a valid Git repository: {target_path}"
            sm.transition_to(TaskState.FAILED)
            t["state"] = sm.current_state
            t["updated_at"] = datetime.now(timezone.utc)
            return get_task(task_id)

        git_mgr = GitWorkspaceManager(target_path, branch_prefix=settings.ai_branch_prefix)
        try:
            git_mgr.squash_merge(task_id, base_branch=t["base_branch"])
            sm.transition_to(TaskState.MERGED)
        except Exception as e:
            t["error_message"] = f"Squash merge failed: {e}"
            sm.transition_to(TaskState.FAILED)

    t["state"] = sm.current_state
    t["updated_at"] = datetime.now(timezone.utc)
    return get_task(task_id)


@app.get("/api/v1/tasks/{task_id}/diff", response_model=DiffSummary, tags=["Tasks"])
def get_task_diff(task_id: str):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    t = tasks_db[task_id]
    if not t["diff_summary"]:
        return DiffSummary()
    return t["diff_summary"]


@app.get("/api/v1/tasks/{task_id}/events", tags=["Streaming"])
async def stream_task_events(task_id: str):
    """Server-Sent Events (SSE) stream for real-time logs and state updates."""
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")

    async def event_generator():
        t = tasks_db[task_id]
        yield f"event: state\ndata: {json.dumps({'state': t['state_machine'].current_state.value})}\n\n"
        await asyncio.sleep(0.5)
        yield f"event: log\ndata: {json.dumps({'message': 'Task initialized in workspace.'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ==========================================
# Typer CLI Entrypoint
# ==========================================
cli_app = typer.Typer(help="Continuum Vibe Server & CLI Orchestrator")


@cli_app.command()
def doctor(
    port: int = typer.Option(8080, help="Target port to check"),
    workspace: str = typer.Option(str(settings.default_workspace_root), help="Workspace root path to verify")
):
    """Runs a complete system preflight diagnostics check (SkyBrain aligned)."""
    console.print("[bold cyan]🩺 Running Continuum System Preflight Diagnostics...[/bold cyan]\n")
    assessor = PreflightAssessor(target_port=port, workspace_root=Path(workspace))
    report = assessor.run_all_checks()

    table = Table(title="Preflight Diagnostic Checkpoints")
    table.add_column("Checkpoint", style="cyan")
    table.add_column("Status", style="bold")
    table.add_column("Details", style="dim")
    table.add_column("Resolution Guide", style="yellow")

    for c in report.checks:
        if c.status == CheckStatus.PASSED:
            status_badge = "[green]PASSED[/green]"
        elif c.status == CheckStatus.WARNING:
            status_badge = "[yellow]WARNING[/yellow]"
        else:
            status_badge = "[bold red]FAILED[/bold red]"
        
        res_str = c.resolution or "-"
        table.add_row(c.name, status_badge, c.message, res_str)

    console.print(table)
    if report.allowed:
        if report.has_warnings:
            console.print(f"\n[bold yellow]⚠️ {report.summary}[/bold yellow]")
        else:
            console.print(f"\n[bold green]✅ {report.summary}[/bold green]")
    else:
        console.print(f"\n[bold red]❌ {report.summary}[/bold red]")
        console.print("[red]Please address the FAILED checkpoints above before running Continuum.[/red]")


@cli_app.command()
def start(
    host: str = typer.Option("0.0.0.0", help="Host address to bind"),
    port: int = typer.Option(8080, help="Port to listen on"),
    reload: bool = typer.Option(False, help="Enable live auto-reload"),
    skip_preflight: bool = typer.Option(False, help="Skip preflight environment diagnostics")
):
    """Starts the Continuum Vibe Server with automated preflight diagnostics."""
    if not skip_preflight:
        console.print("[dim]🔍 Running preflight diagnostics...[/dim]")
        assessor = PreflightAssessor(target_port=port, workspace_root=settings.default_workspace_root)
        report = assessor.run_all_checks()
        if not report.allowed:
            console.print("[bold red]❌ Preflight Check Failed! Aborting server start.[/bold red]")
            for c in report.checks:
                if c.status == CheckStatus.FAILED:
                    console.print(f"  • [red]{c.name}: {c.message}[/red] ➔ [yellow]{c.resolution}[/yellow]")
            console.print("\n[dim]Tip: Use `continuum doctor` for full report or `--skip-preflight` to bypass.[/dim]")
            raise typer.Exit(code=1)
        elif report.has_warnings:
            console.print("[yellow]⚠️ Preflight Check passed with warnings (check `continuum doctor`).[/yellow]")
        else:
            console.print("[green]✅ Preflight Check passed (Zero Config Ready).[/green]")

    console.print(f"[bold cyan]🌌 Starting Continuum Vibe Server on {host}:{port}...[/bold cyan]")
    uvicorn.run("vibe_server.main:app", host=host, port=port, reload=reload)


@cli_app.command()
def review(prompt: str = typer.Argument(..., help="Prompt instruction to review via 5-Lens (SkyBrain aligned)")):
    """Runs an immediate 5-Lens analysis on a prompt via terminal."""
    console.print(f"[bold yellow]🔍 Running 5-Lens Review (SkyBrain aligned) for prompt:[/bold yellow] [italic]{prompt}[/italic]\n")
    report = lens_engine.evaluate(prompt)
    
    table = Table(title="5-Lens Evaluation Results (SkyBrain Aligned)")
    table.add_column("Lens", style="cyan")
    table.add_column("Passed", style="bold")
    table.add_column("Score", justify="right")
    table.add_column("Key Findings", style="dim")

    for name, ev in report.evaluations.items():
        status_str = "[green]PASSED[/green]" if ev.passed else "[red]FAILED[/red]"
        findings_str = "; ".join(f.description for f in ev.findings) if ev.findings else "Clean"
        table.add_row(ev.lens_name, status_str, f"{ev.score}/100", findings_str)

    console.print(table)
    console.print(f"\n[bold]Overall Summary:[/bold] {report.summary}")


if __name__ == "__main__":
    cli_app()
