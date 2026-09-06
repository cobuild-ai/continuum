"""Unit tests for ProjectProvisioner."""
import subprocess
from pathlib import Path
from vibe_server.core.project_provisioner import ProjectProvisioner


def test_provision_new_python_project(tmp_path: Path):
    proj_dir = tmp_path / "new_sample_app"
    proj_dir.mkdir()
    (proj_dir / "main.py").write_text("print('test')\n")

    # Ensure git repository
    success = ProjectProvisioner.ensure_git_repository(proj_dir)
    assert success is True

    # Check .git exists
    assert (proj_dir / ".git").exists()

    # Check .gitignore was provisioned with python rules
    gitignore = proj_dir / ".gitignore"
    assert gitignore.exists()
    assert "__pycache__" in gitignore.read_text()

    # Check git status is clean after initial commit
    res = subprocess.run(["git", "status", "--porcelain"], cwd=proj_dir, capture_output=True, text=True)
    assert res.returncode == 0
    assert len(res.stdout.strip()) == 0


def test_provision_new_android_project(tmp_path: Path):
    proj_dir = tmp_path / "new_android_app"
    proj_dir.mkdir()
    (proj_dir / "build.gradle.kts").write_text("// gradle build\n")

    success = ProjectProvisioner.ensure_git_repository(proj_dir)
    assert success is True

    gitignore = proj_dir / ".gitignore"
    assert gitignore.exists()
    assert ".gradle" in gitignore.read_text()
    assert "*.apk" in gitignore.read_text()
