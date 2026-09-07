"""Unit tests for FastAPI REST endpoints."""
from pathlib import Path
from fastapi.testclient import TestClient
from vibe_server.main import app
from vibe_server.core.states import TaskState

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Continuum" in data["service"]
    assert data["ai_engine"]["model"] == "gemini-3.8-flash"


def test_task_lifecycle_api_flow(tmp_path: Path):
    from vibe_server.core.project_provisioner import ProjectProvisioner
    ProjectProvisioner.ensure_git_repository(tmp_path)

    # 1. Create task
    create_payload = {
        "prompt": "Create helper.py with an add function",
        "target_repo_path": str(tmp_path),
        "base_branch": "main"
    }
    res = client.post("/api/v1/tasks", json=create_payload)
    assert res.status_code == 201
    task = res.json()
    task_id = task["id"]
    assert task["state"] == TaskState.AWAITING_DESIGN_APPROVAL.value
    assert task["lens_report"] is not None
    assert task["lens_report"]["overall_passed"] is True

    # 2. Get task detail
    res = client.get(f"/api/v1/tasks/{task_id}")
    assert res.status_code == 200
    assert res.json()["id"] == task_id

    # 3. Approve design stage -> proceeds to execution & merge approval
    approve_payload = {"approved": True}
    res = client.post(f"/api/v1/tasks/{task_id}/approve", json=approve_payload)
    assert res.status_code == 200
    task_after_design = res.json()
    assert task_after_design["state"] == TaskState.AWAITING_MERGE_APPROVAL.value
    assert task_after_design["diff_summary"] is not None

    # 4. Check Diff endpoint
    res = client.get(f"/api/v1/tasks/{task_id}/diff")
    assert res.status_code == 200
    diff_data = res.json()
    assert diff_data["total_files_changed"] >= 0

    # 5. Final Merge approval -> MERGED
    res = client.post(f"/api/v1/tasks/{task_id}/approve", json=approve_payload)
    assert res.status_code == 200
    assert res.json()["state"] == TaskState.MERGED.value


def test_task_rejection():
    # Create task
    res = client.post("/api/v1/tasks", json={"prompt": "Some experimental idea"})
    task_id = res.json()["id"]

    # Reject
    res = client.post(f"/api/v1/tasks/{task_id}/approve", json={"approved": False, "feedback": "Need redesign"})
    assert res.status_code == 200
    assert res.json()["state"] == TaskState.REJECTED.value


def test_project_discovery_and_active():
    # 1. Discover projects
    res = client.get("/api/v1/projects")
    assert res.status_code == 200
    projects = res.json()
    assert isinstance(projects, list)
    assert len(projects) >= 1

    # 2. Get active project
    res = client.get("/api/v1/projects/active")
    assert res.status_code == 200
    active = res.json()
    assert "name" in active
    assert "path" in active
