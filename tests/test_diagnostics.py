"""Unit tests for Preflight Diagnostics & Checkpoints."""
from pathlib import Path
from vibe_server.core.diagnostics import CheckStatus, PreflightAssessor


def test_preflight_assessor_python_and_git():
    assessor = PreflightAssessor(target_port=8080)
    
    py_check = assessor.check_python_version()
    assert py_check.status == CheckStatus.PASSED
    assert "3.11" in py_check.message
    
    git_check = assessor.check_git_installed()
    assert git_check.status == CheckStatus.PASSED
    assert "git" in git_check.name.lower()


def test_preflight_port_check():
    assessor = PreflightAssessor(target_port=59123)  # Use an ephemeral port unlikely to be in use
    port_check = assessor.check_port_available()
    assert port_check.status == CheckStatus.PASSED


def test_preflight_workspace_check(tmp_path: Path):
    assessor = PreflightAssessor(workspace_root=tmp_path)
    ws_check = assessor.check_workspace_writeable()
    assert ws_check.status == CheckStatus.PASSED


def test_preflight_run_all_checks():
    assessor = PreflightAssessor(target_port=59124)
    report = assessor.run_all_checks()
    assert len(report.checks) >= 5
    assert report.allowed is True  # Python and Git are valid
