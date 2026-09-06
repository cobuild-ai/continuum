"""Host & Sandbox Command Executor: Runs tests and linters with project auto-detection."""
import logging
import os
import re
import shutil
import subprocess
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from vibe_server.sandbox.docker_runner import DockerRunner

logger = logging.getLogger(__name__)


@dataclass
class TestExecutionResult:
    """Structured result of test execution."""
    __test__ = False
    passed: bool
    total: int = 0
    passed_count: int = 0
    failed_count: int = 0
    error_summary: str = ""
    raw_output: str = ""
    command: str = ""
    duration_seconds: float = 0.0
    runner_type: str = "host"  # "docker" or "host"


class HostExecutor:
    """Executes commands and tests inside the workspace using Docker or safe host fallback."""

    def __init__(self, docker_runner: Optional[DockerRunner] = None, timeout_seconds: int = 120):
        self.docker_runner = docker_runner or DockerRunner(timeout_seconds=timeout_seconds)
        self.timeout_seconds = timeout_seconds

    def detect_project_type(self, workspace_path: Path) -> str:
        """Detects the tech stack of the given project path."""
        if (workspace_path / "pyproject.toml").exists() or (workspace_path / "requirements.txt").exists():
            return "python"
        if (workspace_path / "build.gradle.kts").exists() or (workspace_path / "build.gradle").exists() or (workspace_path / "gradlew").exists():
            return "gradle"
        if (workspace_path / "package.json").exists():
            return "node"
        if (workspace_path / "go.mod").exists():
            return "go"
        if (workspace_path / "Cargo.toml").exists():
            return "rust"
        return "unknown"

    def get_test_command(self, workspace_path: Path) -> List[str]:
        """Returns the appropriate test command for the project."""
        ptype = self.detect_project_type(workspace_path)
        if ptype == "python":
            # Check for uv or pytest
            if (workspace_path / ".venv" / "bin" / "pytest").exists():
                return [str(workspace_path / ".venv" / "bin" / "pytest"), "-q"]
            if shutil.which("uv") is not None:
                return ["uv", "run", "pytest", "-q"]
            if shutil.which("pytest") is not None:
                return ["pytest", "-q"]
            return ["python3", "-m", "unittest", "discover"]

        if ptype == "gradle":
            gradlew = workspace_path / "gradlew"
            if gradlew.exists() and os.access(gradlew, os.X_OK):
                return ["./gradlew", "test", "--daemon"]
            elif gradlew.exists():
                return ["sh", "./gradlew", "test", "--daemon"]
            return ["gradle", "test"]

        if ptype == "node":
            return ["npm", "test"]

        if ptype == "go":
            return ["go", "test", "./..."]

        if ptype == "rust":
            return ["cargo", "test"]

        return ["echo", "No automated test suite detected."]

    def run_tests(self, workspace_path: Path) -> TestExecutionResult:
        """Runs the project's test suite and parses output into a structured TestExecutionResult."""
        cmd = self.get_test_command(workspace_path)
        start_time = time.time()
        
        runner_type = "host"
        try:
            # We prefer running via DockerRunner if configured, or host fallback
            # DockerRunner already implements safe fallback if docker is not running
            returncode, stdout, stderr = self.docker_runner.execute_in_sandbox(
                workspace_path=workspace_path,
                command=cmd,
                dry_run=not self.docker_runner.is_docker_available
            )
            runner_type = "docker" if self.docker_runner.is_docker_available else "host"
        except Exception as e:
            duration = time.time() - start_time
            return TestExecutionResult(
                passed=False,
                total=0,
                passed_count=0,
                failed_count=1,
                error_summary=str(e),
                raw_output=str(e),
                command=" ".join(cmd),
                duration_seconds=round(duration, 2),
                runner_type=runner_type
            )

        duration = time.time() - start_time
        combined_output = (stdout + "\n" + stderr).strip()
        
        ptype = self.detect_project_type(workspace_path)
        parsed = self._parse_test_output(ptype, returncode, combined_output)
        parsed.command = " ".join(cmd)
        parsed.duration_seconds = round(duration, 2)
        parsed.raw_output = combined_output
        parsed.runner_type = runner_type
        return parsed

    def _parse_test_output(self, ptype: str, returncode: int, output: str) -> TestExecutionResult:
        """Parses output into counts and error summary based on project type."""
        passed = (returncode == 0)
        total = 0
        passed_count = 0
        failed_count = 0
        error_summary = ""

        if ptype == "python":
            # Pytest output examples:
            # "28 passed in 1.23s"
            # "2 passed, 1 failed in 0.5s"
            pass_match = re.search(r'(\d+)\s+passed', output)
            fail_match = re.search(r'(\d+)\s+failed', output)
            error_match = re.search(r'(\d+)\s+error', output)
            
            if pass_match:
                passed_count = int(pass_match.group(1))
            if fail_match:
                failed_count += int(fail_match.group(1))
            if error_match:
                failed_count += int(error_match.group(1))

            total = passed_count + failed_count

            # Extract failure messages or short summary
            if not passed:
                fail_lines = []
                capture = False
                for line in output.splitlines():
                    if "FAILED" in line or "ERROR" in line or "FAILURES" in line or "ERRORS" in line:
                        capture = True
                    if capture:
                        fail_lines.append(line)
                        if len(fail_lines) >= 20:
                            break
                error_summary = "\n".join(fail_lines) if fail_lines else output[-500:]

        elif ptype == "gradle":
            # Gradle test summary:
            # "BUILD SUCCESSFUL" or "BUILD FAILED"
            # "3 tests completed, 1 failed"
            match = re.search(r'(\d+)\s+tests?\s+completed(?:,\s*(\d+)\s+failed)?', output)
            if match:
                total = int(match.group(1))
                failed_count = int(match.group(2)) if match.group(2) else 0
                passed_count = max(0, total - failed_count)
            else:
                passed_count = 1 if passed else 0
                failed_count = 0 if passed else 1
                total = passed_count + failed_count

            if not passed:
                error_summary = output[-500:]

        elif ptype == "node":
            # Jest / npm test:
            # "Tests:       1 failed, 4 passed, 5 total"
            match = re.search(r'Tests:\s+(?:(\d+)\s+failed,\s*)?(\d+)\s+passed(?:,\s*(\d+)\s+total)?', output)
            if match:
                failed_count = int(match.group(1)) if match.group(1) else 0
                passed_count = int(match.group(2)) if match.group(2) else 0
                total = int(match.group(3)) if match.group(3) else (passed_count + failed_count)
            else:
                passed_count = 1 if passed else 0
                failed_count = 0 if passed else 1
                total = passed_count + failed_count

            if not passed:
                error_summary = output[-500:]

        else:
            # Generic
            passed_count = 1 if passed else 0
            failed_count = 0 if passed else 1
            total = 1
            if not passed:
                error_summary = output[-500:]

        return TestExecutionResult(
            passed=passed,
            total=total,
            passed_count=passed_count,
            failed_count=failed_count,
            error_summary=error_summary
        )
