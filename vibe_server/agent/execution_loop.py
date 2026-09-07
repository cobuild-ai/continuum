"""Autonomous Multi-Turn Agent Execution Loop with Test Feedback & Self-Healing."""
import json
import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from vibe_server.agent.tools import WorkspaceTools
from vibe_server.core.ai_client import AIEngineClient
from vibe_server.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class AgentExecutionResult:
    """Outcome of the multi-turn agent execution loop."""
    task_id: str
    modified_files: List[str] = field(default_factory=list)
    verified: bool = False
    iterations: int = 1
    test_result: Optional[Dict[str, Any]] = None
    summary: str = ""
    logs: List[str] = field(default_factory=list)


SYSTEM_AGENT_PROMPT = (
    "You are Antigravity, an expert autonomous software engineer working within an isolated workspace.\n"
    "Your objective is to satisfy the user's task prompt, write or modify clean code, and verify it with automated tests.\n\n"
    "You have access to the following tools via JSON actions:\n"
    "1. view_file: {\"action\": \"view_file\", \"args\": {\"rel_path\": \"path/file.py\", \"start_line\": 1, \"end_line\": 100}}\n"
    "2. search_code: {\"action\": \"search_code\", \"args\": {\"query\": \"class Example\"}}\n"
    "3. edit_file_block: {\"action\": \"edit_file_block\", \"args\": {\"rel_path\": \"path/file.py\", \"target_block\": \"exact code to replace\", \"replacement_block\": \"new code\"}}\n"
    "4. write_new_file: {\"action\": \"write_new_file\", \"args\": {\"rel_path\": \"path/file.py\", \"content\": \"full code content\"}}\n"
    "5. run_project_tests: {\"action\": \"run_project_tests\", \"args\": {}}\n"
    "6. finish: {\"action\": \"finish\", \"args\": {\"summary\": \"Brief explanation of what was implemented and verified\"}}\n\n"
    "GUIDELINES:\n"
    "- Always think step-by-step.\n"
    "- Output exactly ONE tool call JSON object per turn (e.g. {\"action\": \"...\", \"args\": {...}}).\n"
    "- After writing code or test cases, run 'run_project_tests' to verify.\n"
    "- If tests fail, analyze the error output and use 'edit_file_block' or 'write_new_file' to self-heal the issue.\n"
    "- When tests pass or code is complete, output {\"action\": \"finish\", \"args\": {\"summary\": \"...\"}}."
)


class AutonomousAgentLoop:
    """Orchestrates multi-turn ReAct execution with tool dispatch and compiler/test feedback."""

    def __init__(self, ai_client: Optional[AIEngineClient] = None, max_turns: int = 4):
        self.ai_client = ai_client or AIEngineClient.from_settings(settings)
        self.max_turns = max_turns

    def run(self, workspace_path: Path, prompt: str, task_id: str) -> AgentExecutionResult:
        """Executes the multi-turn agent loop in the workspace."""
        tools = WorkspaceTools(workspace_path)
        history: List[Dict[str, str]] = []
        modified_files: List[str] = []
        logs: List[str] = []
        last_test_result: Optional[Dict[str, Any]] = None
        turn = 0

        initial_user_msg = (
            f"User Task: {prompt}\n\n"
            f"Please inspect the workspace if needed, implement the changes, run tests to verify, and finish."
        )
        current_input = initial_user_msg

        logger.info(f"Starting AutonomousAgentLoop for task {task_id} in {workspace_path}")

        while turn < self.max_turns:
            turn += 1
            logs.append(f"--- Turn {turn}/{self.max_turns} ---")
            
            # 1. Ask AI for next step
            response_text = self.ai_client.generate_chat(
                system_prompt=SYSTEM_AGENT_PROMPT,
                user_prompt=current_input,
                history=history
            )
            logs.append(f"Agent response: {response_text[:200]}...")

            # 2. Parse tool action
            action_data = self._parse_action(response_text)

            # Fallback handling: If model generated markdown code blocks instead of JSON tool call
            if not action_data:
                code_files = self._extract_code_blocks(response_text)
                if code_files:
                    for rel_p, code_content in code_files.items():
                        res = tools.write_new_file(rel_p, code_content)
                        if rel_p not in modified_files:
                            modified_files.append(rel_p)
                        logs.append(f"Auto-wrote file {rel_p}: {res}")
                    # Run tests after writing
                    test_res = tools.run_project_tests()
                    last_test_result = test_res
                    logs.append(f"Automated test run: passed={test_res['passed']}, total={test_res['total']}")
                    if test_res["passed"]:
                        return AgentExecutionResult(
                            task_id=task_id,
                            modified_files=modified_files,
                            verified=True,
                            iterations=turn,
                            test_result=test_res,
                            summary=f"Code implemented and verified against {test_res['passed_count']} tests.",
                            logs=logs
                        )
                    else:
                        # Feed error to next turn for self-healing
                        current_input = (
                            f"Automated test failed with command: {test_res['command']}\n"
                            f"Error summary:\n{test_res['error_summary']}\n\n"
                            f"Please fix the code or test to resolve this failure."
                        )
                        history.append({"role": "user", "content": current_input})
                        continue
                else:
                    # Could not parse action
                    logs.append("Warning: Could not parse action from agent response.")
                    break

            action_name = action_data.get("action")
            args = action_data.get("args", {})

            # Execute tool
            if action_name == "view_file":
                out = tools.view_file(
                    args.get("rel_path", ""),
                    args.get("start_line", 1),
                    args.get("end_line", 100)
                )
                current_input = f"Tool Output (view_file):\n{out}"
                logs.append(f"Viewed file {args.get('rel_path')}")

            elif action_name == "search_code":
                out = tools.search_code(args.get("query", ""), args.get("rel_dir", ""))
                current_input = f"Tool Output (search_code):\n{out}"
                logs.append(f"Searched code for '{args.get('query')}'")

            elif action_name == "write_new_file":
                rel_p = args.get("rel_path", "")
                content = args.get("content", "")
                out = tools.write_new_file(rel_p, content)
                if rel_p and rel_p not in modified_files:
                    modified_files.append(rel_p)
                current_input = f"Tool Output (write_new_file):\n{out}"
                logs.append(f"Wrote file {rel_p}")

            elif action_name == "edit_file_block":
                rel_p = args.get("rel_path", "")
                t_block = args.get("target_block", "")
                r_block = args.get("replacement_block", "")
                out = tools.edit_file_block(rel_p, t_block, r_block)
                if rel_p and rel_p not in modified_files:
                    modified_files.append(rel_p)
                current_input = f"Tool Output (edit_file_block):\n{out}"
                logs.append(f"Edited file block in {rel_p}")

            elif action_name == "run_project_tests":
                test_res = tools.run_project_tests()
                last_test_result = test_res
                current_input = (
                    f"Tool Output (run_project_tests):\n"
                    f"Passed: {test_res['passed']}\n"
                    f"Total: {test_res['total']}, Passed Count: {test_res['passed_count']}, Failed Count: {test_res['failed_count']}\n"
                    f"Error Summary:\n{test_res['error_summary']}\n"
                    f"Command: {test_res['command']}"
                )
                logs.append(f"Ran tests: passed={test_res['passed']}, total={test_res['total']}, failed={test_res['failed_count']}")

            elif action_name == "finish":
                summary = args.get("summary", "Task completed.")
                logs.append(f"Agent finished: {summary}")
                # Perform final test verification check if not checked yet
                if last_test_result is None:
                    last_test_result = tools.run_project_tests()

                return AgentExecutionResult(
                    task_id=task_id,
                    modified_files=modified_files,
                    verified=bool(last_test_result and last_test_result.get("passed", False)),
                    iterations=turn,
                    test_result=last_test_result,
                    summary=summary,
                    logs=logs
                )

            else:
                current_input = f"Unknown action: '{action_name}'. Available actions: view_file, search_code, edit_file_block, write_new_file, run_project_tests, finish."
                logs.append(f"Unknown action {action_name}")

            history.append({"role": "model", "content": response_text})
            history.append({"role": "user", "content": current_input})

        # Completed maximum turns
        if last_test_result is None:
            last_test_result = tools.run_project_tests()

        verified = bool(last_test_result and last_test_result.get("passed", False))
        return AgentExecutionResult(
            task_id=task_id,
            modified_files=modified_files,
            verified=verified,
            iterations=turn,
            test_result=last_test_result,
            summary=f"Agent loop finished after {turn} turns (verified={verified}).",
            logs=logs
        )

    def _parse_action(self, text: str) -> Optional[Dict[str, Any]]:
        """Extracts JSON action from agent response."""
        clean_text = re.sub(r"^<think>.*?</think>", "", text, flags=re.DOTALL).strip()
        
        # Try finding json block
        json_match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", clean_text, re.DOTALL)
        if json_match:
            try:
                return json.loads(json_match.group(1))
            except Exception:
                pass

        # Try raw json matching
        match = re.search(r"\{\s*\"action\"\s*:\s*\"[a-zA-Z0-9_]+\".*\}", clean_text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except Exception:
                pass

        return None

    def _extract_code_blocks(self, text: str) -> Dict[str, str]:
        """Extracts markdown code blocks if agent directly answered with code."""
        clean_text = re.sub(r"^<think>.*?</think>", "", text, flags=re.DOTALL).strip()
        files = {}
        for block in re.finditer(r"```([a-zA-Z0-9_\-]+)?\s*(?:#|//)?\s*(?:filename:)?\s*([a-zA-Z0-9_./\-]+)?\n(.*?)```", clean_text, re.DOTALL):
            fname = block.group(2)
            content = block.group(3)
            if fname:
                files[fname.strip()] = content
        return files
