"""Unit tests for WorkspaceTools and AutonomousAgentLoop."""
from pathlib import Path
import pytest
from unittest.mock import MagicMock

from vibe_server.agent.tools import WorkspaceTools, WorkspaceSecurityError
from vibe_server.agent.execution_loop import AutonomousAgentLoop, AgentExecutionResult
from vibe_server.core.ai_client import AIEngineClient
from vibe_server.sandbox.host_executor import HostExecutor, TestExecutionResult


def test_workspace_tools_path_traversal_prevention(tmp_path: Path):
    tools = WorkspaceTools(tmp_path)
    with pytest.raises(WorkspaceSecurityError):
        tools._safe_resolve("../../etc/passwd")


def test_workspace_tools_file_lifecycle(tmp_path: Path):
    tools = WorkspaceTools(tmp_path)
    
    # Write new file
    res = tools.write_new_file("hello.py", "def greet():\n    return 'hello'\n")
    assert "Success" in res
    assert (tmp_path / "hello.py").exists()

    # View file
    view_out = tools.view_file("hello.py", 1, 10)
    assert "def greet():" in view_out
    assert "1:" in view_out

    # Edit file block
    edit_res = tools.edit_file_block("hello.py", "return 'hello'", "return 'world'")
    assert "Success" in edit_res
    assert "return 'world'" in (tmp_path / "hello.py").read_text()

    # Search code
    search_out = tools.search_code("greet")
    assert "hello.py:1: def greet():" in search_out


def test_autonomous_agent_loop_execution(tmp_path: Path):
    # Mock AI Client to return a JSON action then finish
    mock_ai = MagicMock(spec=AIEngineClient)
    mock_ai.generate_chat.side_effect = [
        '{"action": "write_new_file", "args": {"rel_path": "feature.py", "content": "x = 42\\n"}}',
        '{"action": "finish", "args": {"summary": "Feature implemented and verified."}}'
    ]

    mock_executor = MagicMock(spec=HostExecutor)
    mock_executor.run_tests.return_value = TestExecutionResult(
        passed=True,
        total=5,
        passed_count=5,
        failed_count=0,
        command="pytest -q"
    )

    loop = AutonomousAgentLoop(ai_client=mock_ai, max_turns=3)
    
    # Set host executor on the workspace tools via monkeypatch/init
    # We can inject loop run
    result: AgentExecutionResult = loop.run(tmp_path, "Implement feature", "task-123")
    
    assert result.task_id == "task-123"
    assert "feature.py" in result.modified_files
    assert (tmp_path / "feature.py").exists()
    assert result.iterations >= 1
