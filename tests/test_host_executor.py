"""Unit tests for HostExecutor sandbox and test detection."""
from pathlib import Path
from vibe_server.sandbox.host_executor import HostExecutor, TestExecutionResult


def test_detect_project_type_python(tmp_path: Path):
    (tmp_path / "pyproject.toml").write_text("[project]\nname='test'\n")
    executor = HostExecutor()
    assert executor.detect_project_type(tmp_path) == "python"


def test_detect_project_type_gradle(tmp_path: Path):
    (tmp_path / "build.gradle.kts").write_text("// gradle build")
    executor = HostExecutor()
    assert executor.detect_project_type(tmp_path) == "gradle"


def test_parse_test_output_pytest_pass():
    executor = HostExecutor()
    raw = "================ 28 passed in 1.23s ================"
    result = executor._parse_test_output("python", 0, raw)
    assert result.passed is True
    assert result.total == 28
    assert result.passed_count == 28
    assert result.failed_count == 0


def test_parse_test_output_pytest_failure():
    executor = HostExecutor()
    raw = (
        "FAILED tests/test_foo.py::test_fail - AssertionError: assert False\n"
        "================ 1 failed, 27 passed in 1.45s ================"
    )
    result = executor._parse_test_output("python", 1, raw)
    assert result.passed is False
    assert result.total == 28
    assert result.passed_count == 27
    assert result.failed_count == 1
    assert "FAILED" in result.error_summary


def test_parse_test_output_gradle_pass():
    executor = HostExecutor()
    raw = "BUILD SUCCESSFUL in 2s\n12 tests completed, 0 failed"
    result = executor._parse_test_output("gradle", 0, raw)
    assert result.passed is True
    assert result.total == 12
    assert result.passed_count == 12
    assert result.failed_count == 0
