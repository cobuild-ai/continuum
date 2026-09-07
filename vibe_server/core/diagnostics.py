"""Continuum Preflight Diagnostics Engine — aligned with SkyBrain Preflight Architecture."""
import enum
import os
import platform
import shutil
import socket
import subprocess
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional


class CheckStatus(str, enum.Enum):
    PASSED = "PASSED"
    WARNING = "WARNING"
    FAILED = "FAILED"


@dataclass
class CheckItem:
    """A single diagnostic checkpoint result."""
    name: str
    status: CheckStatus
    message: str
    resolution: Optional[str] = None


@dataclass
class PreflightReport:
    """Consolidated preflight diagnostic report."""
    allowed: bool
    checks: List[CheckItem] = field(default_factory=list)
    has_warnings: bool = False
    has_failures: bool = False

    @property
    def summary(self) -> str:
        if not self.allowed:
            return "Preflight check failed. Critical dependencies missing."
        if self.has_warnings:
            return "Preflight check passed with warnings. Some optional features may be degraded."
        return "All system preflight checks passed successfully."


class PreflightAssessor:
    """Evaluates host system readiness before Continuum Vibe Server startup."""

    def __init__(self, target_port: int = 8080, workspace_root: Optional[Path] = None):
        self.target_port = target_port
        self.workspace_root = workspace_root or Path("/Users/smilelife/Projects/OSSProject")

    def check_python_version(self) -> CheckItem:
        major, minor = sys.version_info.major, sys.version_info.minor
        version_str = f"{major}.{minor}.{sys.version_info.micro}"
        if major >= 3 and minor >= 11:
            return CheckItem(
                name="Python Runtime",
                status=CheckStatus.PASSED,
                message=f"Python {version_str} meets >= 3.11 requirement."
            )
        return CheckItem(
            name="Python Runtime",
            status=CheckStatus.FAILED,
            message=f"Python {version_str} is below required 3.11+.",
            resolution="Upgrade Python to 3.11+ or run using `uv run python`."
        )

    def check_git_installed(self) -> CheckItem:
        git_path = shutil.which("git")
        if not git_path:
            return CheckItem(
                name="Git Toolchain",
                status=CheckStatus.FAILED,
                message="Git binary not found on system PATH.",
                resolution="Install git via Homebrew: `brew install git`."
            )
        try:
            res = subprocess.run(["git", "--version"], capture_output=True, text=True, timeout=3)
            return CheckItem(
                name="Git Toolchain",
                status=CheckStatus.PASSED,
                message=f"Installed ({res.stdout.strip()})."
            )
        except Exception as e:
            return CheckItem(
                name="Git Toolchain",
                status=CheckStatus.FAILED,
                message=f"Git check failed: {str(e)}",
                resolution="Ensure git is functional in your shell."
            )

    def check_docker_sandbox(self) -> CheckItem:
        docker_path = shutil.which("docker")
        if not docker_path:
            return CheckItem(
                name="Docker Sandbox",
                status=CheckStatus.WARNING,
                message="Docker CLI not found. Local subprocess fallback will be active.",
                resolution="Install Docker Desktop or Podman to enable full container isolation."
            )
        try:
            res = subprocess.run(
                ["docker", "info"],
                capture_output=True,
                text=True,
                timeout=4
            )
            if res.returncode == 0:
                return CheckItem(
                    name="Docker Sandbox",
                    status=CheckStatus.PASSED,
                    message="Docker daemon is active and responsive."
                )
            return CheckItem(
                name="Docker Sandbox",
                status=CheckStatus.WARNING,
                message="Docker daemon is not running. Local subprocess fallback will be used.",
                resolution="Start Docker Desktop app to enable volume-mounted sandboxing."
            )
        except subprocess.TimeoutExpired:
            return CheckItem(
                name="Docker Sandbox",
                status=CheckStatus.WARNING,
                message="Docker daemon check timed out. Running in fallback mode.",
                resolution="Check Docker Desktop resource usage or restart Docker."
            )
        except Exception as e:
            return CheckItem(
                name="Docker Sandbox",
                status=CheckStatus.WARNING,
                message=f"Docker warning: {str(e)}",
                resolution="Verify docker daemon status."
            )

    def check_port_available(self) -> CheckItem:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            try:
                s.bind(("0.0.0.0", self.target_port))
                return CheckItem(
                    name="Port Availability",
                    status=CheckStatus.PASSED,
                    message=f"Port {self.target_port} is free and ready to bind."
                )
            except OSError:
                return CheckItem(
                    name="Port Availability",
                    status=CheckStatus.FAILED,
                    message=f"Port {self.target_port} is already in use by another process.",
                    resolution=f"Stop the conflicting process on port {self.target_port} or run with `--port <PORT>`."
                )

    def check_workspace_writeable(self) -> CheckItem:
        target = self.workspace_root
        if not target.exists():
            return CheckItem(
                name="Workspace Root",
                status=CheckStatus.WARNING,
                message=f"Workspace path {target} does not exist yet.",
                resolution=f"Directory will be created upon first task."
            )
        if os.access(target, os.W_OK):
            return CheckItem(
                name="Workspace Root",
                status=CheckStatus.PASSED,
                message=f"Workspace {target} is fully accessible and writable."
            )
        return CheckItem(
            name="Workspace Root",
            status=CheckStatus.FAILED,
            message=f"Workspace {target} has no write permission.",
            resolution=f"Adjust permissions: `chmod +w {target}`."
        )

    def check_ai_engine(self) -> CheckItem:
        from vibe_server.core.config import settings
        from vibe_server.core.ai_client import AIEngineClient
        client = AIEngineClient()
        has_key = bool(client.gemini_api_key)
        return CheckItem(
            name="AI Engine Model",
            status=CheckStatus.PASSED,
            message=f"Configured: {settings.gemini_model} (Provider: {settings.ai_provider}, API Key: {'Active' if has_key else 'Fallback to Local SkyBrain'})",
            resolution=None
        )

    def run_all_checks(self) -> PreflightReport:
        checks = [
            self.check_python_version(),
            self.check_git_installed(),
            self.check_docker_sandbox(),
            self.check_port_available(),
            self.check_workspace_writeable(),
            self.check_ai_engine()
        ]

        has_failures = any(c.status == CheckStatus.FAILED for c in checks)
        has_warnings = any(c.status == CheckStatus.WARNING for c in checks)
        allowed = not has_failures

        return PreflightReport(
            allowed=allowed,
            checks=checks,
            has_warnings=has_warnings,
            has_failures=has_failures
        )
