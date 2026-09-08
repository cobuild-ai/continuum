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


def test_check_quality_threshold():
    from vibe_server.core.diagnostics import check_quality_threshold
    from vibe_server.core.models import LensReport, LensEvaluation

    # Passing report: all lenses >= 70
    passing = LensReport(
        overall_passed=True,
        average_score=85.0,
        evaluations={
            "CleanCode": LensEvaluation(lens_name="CleanCode", category="clean_code", score=80.0, passed=True),
            "Security": LensEvaluation(lens_name="Security", category="security", score=90.0, passed=True)
        }
    )
    passed, violations = check_quality_threshold(passing, threshold=70.0)
    assert passed is True
    assert len(violations) == 0

    # Failing report: average and one lens below 70
    failing = LensReport(
        overall_passed=True,
        average_score=65.0,
        evaluations={
            "CleanCode": LensEvaluation(lens_name="CleanCode", category="clean_code", score=55.0, passed=True),
            "Security": LensEvaluation(lens_name="Security", category="security", score=75.0, passed=True)
        }
    )
    passed, violations = check_quality_threshold(failing, threshold=70.0)
    assert passed is False
    assert len(violations) >= 2

