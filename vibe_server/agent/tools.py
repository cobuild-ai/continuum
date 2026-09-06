"""Safe workspace-scoped tools for Continuum Autonomous Agent."""
import logging
import os
import re
from pathlib import Path
from typing import Dict, List, Optional

from vibe_server.sandbox.host_executor import HostExecutor, TestExecutionResult

logger = logging.getLogger(__name__)


class WorkspaceSecurityError(PermissionError):
    """Raised when an operation attempts to escape the authorized workspace."""
    pass


class WorkspaceTools:
    """Provides safe, scoped file operations and test execution tools within a project workspace."""

    def __init__(self, workspace_path: Path, host_executor: Optional[HostExecutor] = None):
        self.workspace_path = workspace_path.resolve()
        self.host_executor = host_executor or HostExecutor()

    def _safe_resolve(self, rel_path: str) -> Path:
        """Resolves relative path and verifies it resides strictly within workspace_path."""
        clean_path = Path(rel_path).as_posix().lstrip("/")
        resolved = (self.workspace_path / clean_path).resolve()
        try:
            resolved.relative_to(self.workspace_path)
        except ValueError:
            raise WorkspaceSecurityError(f"Access denied: Path '{rel_path}' escapes workspace '{self.workspace_path}'.")
        return resolved

    def view_file(self, rel_path: str, start_line: int = 1, end_line: int = 150) -> str:
        """Views file content with 1-indexed line numbers."""
        target = self._safe_resolve(rel_path)
        if not target.exists():
            return f"Error: File '{rel_path}' does not exist."
        if target.is_dir():
            return f"Error: '{rel_path}' is a directory."

        try:
            content = target.read_text(encoding="utf-8", errors="replace")
            lines = content.splitlines()
            total_lines = len(lines)
            
            start = max(1, start_line)
            end = min(total_lines, max(start, end_line))
            
            output = [f"--- File: {rel_path} (Lines {start}-{end} of {total_lines}) ---"]
            for idx in range(start, end + 1):
                output.append(f"{idx:4d}: {lines[idx - 1]}")
            return "\n".join(output)
        except Exception as e:
            return f"Error reading file '{rel_path}': {e}"

    def search_code(self, query: str, rel_dir: str = "", max_results: int = 25) -> str:
        """Searches for pattern/text across workspace files."""
        search_root = self._safe_resolve(rel_dir) if rel_dir else self.workspace_path
        if not search_root.exists() or not search_root.is_dir():
            return f"Error: Search directory '{rel_dir}' does not exist."

        results = []
        pattern = re.compile(re.escape(query), re.IGNORECASE)

        for root, dirs, files in os.walk(search_root):
            # Exclude version control and build folders
            dirs[:] = [d for d in dirs if d not in {".git", ".venv", "__pycache__", "build", ".gradle", "node_modules", ".idea"}]
            for fname in files:
                if fname.startswith("."):
                    continue
                file_path = Path(root) / fname
                try:
                    rel = file_path.relative_to(self.workspace_path).as_posix()
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    for line_num, line in enumerate(content.splitlines(), start=1):
                        if pattern.search(line):
                            results.append(f"{rel}:{line_num}: {line.strip()[:120]}")
                            if len(results) >= max_results:
                                break
                except Exception:
                    continue
                if len(results) >= max_results:
                    break
            if len(results) >= max_results:
                break

        if not results:
            return f"No matches found for query: '{query}'"
        return "\n".join(results)

    def write_new_file(self, rel_path: str, content: str) -> str:
        """Creates or overwrites a file with content."""
        target = self._safe_resolve(rel_path)
        try:
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(content, encoding="utf-8")
            return f"Success: Successfully wrote {len(content)} bytes to '{rel_path}'."
        except Exception as e:
            return f"Error writing to '{rel_path}': {e}"

    def edit_file_block(self, rel_path: str, target_block: str, replacement_block: str) -> str:
        """Replaces exact target_block in file with replacement_block."""
        target = self._safe_resolve(rel_path)
        if not target.exists():
            return f"Error: File '{rel_path}' does not exist."

        try:
            content = target.read_text(encoding="utf-8")
            if target_block not in content:
                # Try normalized whitespace
                return f"Error: Target block not found in '{rel_path}'."
            
            occurrences = content.count(target_block)
            if occurrences > 1:
                return f"Error: Target block appears {occurrences} times in '{rel_path}'. Provide more surrounding context."

            new_content = content.replace(target_block, replacement_block, 1)
            target.write_text(new_content, encoding="utf-8")
            return f"Success: Updated '{rel_path}' successfully."
        except Exception as e:
            return f"Error editing '{rel_path}': {e}"

    def run_project_tests(self) -> Dict:
        """Executes real test suite on host/docker sandbox and returns parsed result."""
        result: TestExecutionResult = self.host_executor.run_tests(self.workspace_path)
        return {
            "passed": result.passed,
            "total": result.total,
            "passed_count": result.passed_count,
            "failed_count": result.failed_count,
            "error_summary": result.error_summary,
            "command": result.command,
            "duration_seconds": result.duration_seconds,
            "runner_type": result.runner_type,
            "raw_output": result.raw_output[-1000:] if result.raw_output else ""
        }
