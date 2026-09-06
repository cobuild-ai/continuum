"""End-to-End integration test for Continuum Vibe Server workflow."""
import subprocess
from pathlib import Path
from fastapi.testclient import TestClient
from vibe_server.main import app
from vibe_server.core.states import TaskState

client = TestClient(app)


def test_full_e2e_lifecycle_with_real_git_workspace(tmp_path: Path):
    # 1. Setup a real git repo to act as the target project
    repo_dir = tmp_path / "sample_managed_project"
    repo_dir.mkdir()

    subprocess.run(["git", "init", "-b", "main"], cwd=repo_dir, check=True, capture_output=True)
    subprocess.run(["git", "config", "user.name", "Continuum Tester"], cwd=repo_dir, check=True)
    subprocess.run(["git", "config", "user.email", "tester@continuum.ai"], cwd=repo_dir, check=True)

    readme_file = repo_dir / "README.md"
    readme_file.write_text("# Managed Project\nInitial baseline.")
    subprocess.run(["git", "add", "README.md"], cwd=repo_dir, check=True)
    subprocess.run(["git", "commit", "-m", "chore: initial commit"], cwd=repo_dir, check=True)

    # 2. Submit Task to Continuum Vibe Server
    create_payload = {
        "prompt": "Add high-performance mathematical statistics module and test cases",
        "target_repo_path": str(repo_dir),
        "base_branch": "main"
    }
    res = client.post("/api/v1/tasks", json=create_payload)
    assert res.status_code == 201
    task = res.json()
    task_id = task["id"]

    # Verify SkyBrain 5-Lens Evaluation
    assert task["state"] == TaskState.AWAITING_DESIGN_APPROVAL.value
    report = task["lens_report"]
    assert report is not None
    assert report["overall_passed"] is True
    assert len(report["evaluations"]) == 5

    # 3. Approve Design -> State Machine advances to execution & creates branch
    approve_res = client.post(f"/api/v1/tasks/{task_id}/approve", json={"approved": True})
    assert approve_res.status_code == 200
    task_exec = approve_res.json()
    assert task_exec["state"] == TaskState.AWAITING_MERGE_APPROVAL.value

    # Verify task branch was created in target repo
    branches_res = subprocess.run(["git", "branch"], cwd=repo_dir, check=True, capture_output=True, text=True)
    task_branch = f"ai/{task_id}"
    assert task_branch in branches_res.stdout

    # 4. Simulate Sandbox writing changes to the task branch
    feature_file = repo_dir / "stats.py"
    feature_file.write_text("def calculate_mean(values: list[float]) -> float:\n    return sum(values) / len(values)\n")
    subprocess.run(["git", "add", "stats.py"], cwd=repo_dir, check=True)
    subprocess.run(["git", "commit", "-m", "feat: add stats module"], cwd=repo_dir, check=True)

    # 5. Check Diff API
    diff_res = client.get(f"/api/v1/tasks/{task_id}/diff")
    assert diff_res.status_code == 200

    # 6. One-Touch Squash Merge approval
    merge_res = client.post(f"/api/v1/tasks/{task_id}/approve", json={"approved": True})
    assert merge_res.status_code == 200
    assert merge_res.json()["state"] == TaskState.MERGED.value

    # Verify changes are committed on main and task branch is removed
    curr_branch = subprocess.run(["git", "rev-parse", "--abbrev-ref", "HEAD"], cwd=repo_dir, check=True, capture_output=True, text=True).stdout.strip()
    assert curr_branch == "main"
    assert (repo_dir / "stats.py").exists()

    branches_after = subprocess.run(["git", "branch"], cwd=repo_dir, check=True, capture_output=True, text=True).stdout
    assert task_branch not in branches_after
