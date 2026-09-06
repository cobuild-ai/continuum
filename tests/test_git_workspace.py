"""Unit tests for Git workspace manager."""
import subprocess
from pathlib import Path
import pytest
from vibe_server.sandbox.git_workspace import GitWorkspaceManager


@pytest.fixture
def temp_git_repo(tmp_path: Path):
    repo = tmp_path / "test_repo"
    repo.mkdir()
    
    # Init git repo
    subprocess.run(["git", "init", "-b", "main"], cwd=repo, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "TestUser"], cwd=repo, check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=repo, check=True)
    
    # Initial commit
    init_file = repo / "README.md"
    init_file.write_text("# Test Repo", encoding="utf-8")
    subprocess.run(["git", "add", "README.md"], cwd=repo, check=True)
    subprocess.run(["git", "commit", "-m", "chore: initial commit"], cwd=repo, check=True)
    
    return repo


def test_git_workspace_branch_diff_and_squash(temp_git_repo: Path):
    manager = GitWorkspaceManager(temp_git_repo)
    task_id = "task-101"
    
    # 1. Create task branch
    branch_name = manager.create_task_branch(task_id, base_branch="main")
    assert branch_name == "ai/task-101"
    assert manager.get_current_branch() == "ai/task-101"
    
    # 2. Make changes in task branch
    new_file = temp_git_repo / "feature.py"
    new_file.write_text("print('hello vibe')\n", encoding="utf-8")
    subprocess.run(["git", "add", "feature.py"], cwd=temp_git_repo, check=True)
    subprocess.run(["git", "commit", "-m", "feat: add feature in ai branch"], cwd=temp_git_repo, check=True)
    
    # 3. Get diff
    diff_summary = manager.get_diff(task_id, base_branch="main")
    assert diff_summary.total_files_changed == 1
    assert diff_summary.files[0].filepath == "feature.py"
    assert diff_summary.total_additions == 1
    
    # 4. Squash merge
    success = manager.squash_merge(task_id, base_branch="main", commit_msg="feat: merged ai task")
    assert success is True
    assert manager.get_current_branch() == "main"
    assert (temp_git_repo / "feature.py").exists()
    
    # Verify task branch is deleted
    branches = subprocess.run(["git", "branch"], cwd=temp_git_repo, capture_output=True, text=True).stdout
    assert "ai/task-101" not in branches


def test_git_workspace_discard_branch(temp_git_repo: Path):
    manager = GitWorkspaceManager(temp_git_repo)
    task_id = "task-reject"
    
    manager.create_task_branch(task_id, base_branch="main")
    assert manager.get_current_branch() == "ai/task-reject"
    
    # Discard branch
    discarded = manager.discard_task_branch(task_id, base_branch="main")
    assert discarded is True
    assert manager.get_current_branch() == "main"
    
    branches = subprocess.run(["git", "branch"], cwd=temp_git_repo, capture_output=True, text=True).stdout
    assert "ai/task-reject" not in branches
