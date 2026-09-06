"""Git workspace manager: handles atomic ai/* branch isolation, diff extraction, and squash merging."""
import subprocess
from pathlib import Path
from typing import Optional
from vibe_server.core.models import DiffSummary, FileDiff


class GitWorkspaceError(Exception):
    """Raised when git operations encounter an error."""
    pass


class GitWorkspaceManager:
    """Safely isolates changes into temporary ai/ branches and handles squash merges."""

    def __init__(self, repo_path: Path, branch_prefix: str = "ai/"):
        self.repo_path = repo_path
        self.branch_prefix = branch_prefix

    def _run_git(self, *args: str) -> str:
        res = subprocess.run(
            ["git", *args],
            cwd=self.repo_path,
            capture_output=True,
            text=True
        )
        if res.returncode != 0:
            raise GitWorkspaceError(f"git {' '.join(args)} failed: {res.stderr.strip()}")
        return res.stdout.strip()

    def get_current_branch(self) -> str:
        return self._run_git("rev-parse", "--abbrev-ref", "HEAD")

    def create_task_branch(self, task_id: str, base_branch: str = "main") -> str:
        branch_name = f"{self.branch_prefix}{task_id}"
        # Ensure base branch is active first
        self._run_git("checkout", base_branch)
        # Create and checkout task branch
        self._run_git("checkout", "-b", branch_name)
        return branch_name

    def get_diff(self, task_id: str, base_branch: str = "main") -> DiffSummary:
        branch_name = f"{self.branch_prefix}{task_id}"
        # Get diff stat
        stat_output = self._run_git("diff", "--numstat", f"{base_branch}...{branch_name}")
        
        file_diffs = []
        total_add = 0
        total_del = 0

        for line in stat_output.splitlines():
            parts = line.split("\t")
            if len(parts) >= 3:
                try:
                    add = int(parts[0]) if parts[0] != "-" else 0
                    del_ = int(parts[1]) if parts[1] != "-" else 0
                except ValueError:
                    add, del_ = 0, 0
                
                fpath = parts[2]
                total_add += add
                total_del += del_
                
                patch = self._run_git("diff", f"{base_branch}...{branch_name}", "--", fpath)
                file_diffs.append(FileDiff(
                    filepath=fpath,
                    additions=add,
                    deletions=del_,
                    patch=patch
                ))

        return DiffSummary(
            total_files_changed=len(file_diffs),
            total_additions=total_add,
            total_deletions=total_del,
            files=file_diffs
        )

    def squash_merge(self, task_id: str, base_branch: str = "main", commit_msg: Optional[str] = None) -> bool:
        branch_name = f"{self.branch_prefix}{task_id}"
        msg = commit_msg or f"feat: apply ai changes from task {task_id}"
        
        # Checkout base branch
        self._run_git("checkout", base_branch)
        # Squash merge
        self._run_git("merge", "--squash", branch_name)
        # Commit squashed changes
        self._run_git("commit", "-m", msg)
        # Delete task branch
        self._run_git("branch", "-D", branch_name)
        return True

    def discard_task_branch(self, task_id: str, base_branch: str = "main") -> bool:
        branch_name = f"{self.branch_prefix}{task_id}"
        current = self.get_current_branch()
        if current == branch_name:
            self._run_git("checkout", base_branch)
        self._run_git("branch", "-D", branch_name)
        return True
