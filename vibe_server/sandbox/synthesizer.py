"""Code synthesizer: Leverages local SkyBrain (Qwen 3.8) to generate code changes on isolated task branches."""
import json
import logging
import re
import subprocess
import urllib.request
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from vibe_server.core.ai_client import AIEngineClient
from vibe_server.core.config import settings

from vibe_server.agent.execution_loop import AutonomousAgentLoop, AgentExecutionResult
from vibe_server.core.models import VerificationReport

logger = logging.getLogger(__name__)


class CodeSynthesizer:
    """Generates code from user prompts using Gemini Flash / SkyBrain with autonomous multi-turn loop and test verification."""

    def __init__(
        self,
        ai_client: Optional[AIEngineClient] = None,
        autonomous_loop: Optional[AutonomousAgentLoop] = None
    ):
        self.ai_client = ai_client or AIEngineClient(
            provider=settings.ai_provider,
            gemini_model=settings.gemini_model,
            gemini_api_key=settings.gemini_api_key,
            skybrain_url=settings.skybrain_url,
            skybrain_model=settings.skybrain_model
        )
        self.autonomous_loop = autonomous_loop or AutonomousAgentLoop(ai_client=self.ai_client)

    def execute_and_verify(self, repo_path: Path, prompt: str, task_id: str) -> Tuple[List[str], VerificationReport]:
        """
        Executes the autonomous agent loop in the target repository branch,
        runs test suite verification, and commits changes.
        """
        logger.info(f"Executing autonomous agent loop for task {task_id} on {repo_path}")
        try:
            loop_result: AgentExecutionResult = self.autonomous_loop.run(
                workspace_path=repo_path,
                prompt=prompt,
                task_id=task_id
            )
            
            test_data = loop_result.test_result or {}
            report = VerificationReport(
                verified=loop_result.verified,
                tests_passed=bool(test_data.get("passed", False)),
                total_tests=test_data.get("total", 0),
                passed_tests=test_data.get("passed_count", 0),
                failed_tests=test_data.get("failed_count", 0),
                execution_time_seconds=test_data.get("duration_seconds", 0.0),
                command_run=test_data.get("command", ""),
                summary=loop_result.summary,
                iterations=loop_result.iterations,
                raw_output=test_data.get("raw_output", "")
            )
            modified_files = loop_result.modified_files
        except Exception as loop_err:
            logger.warning(f"Autonomous loop exception: {loop_err}, falling back to direct synthesis")
            modified_files = self.synthesize_and_commit(repo_path, prompt, task_id)
            report = VerificationReport(
                verified=False,
                tests_passed=False,
                summary=f"Synthesized {len(modified_files)} files (fallback). Loop err: {loop_err}",
                iterations=1
            )

        # Ensure all working tree changes are committed to the task branch
        try:
            status_res = subprocess.run(["git", "status", "--porcelain"], cwd=repo_path, capture_output=True, text=True)
            if status_res.stdout.strip():
                subprocess.run(["git", "add", "-A"], cwd=repo_path, check=True, capture_output=True)
                verified_tag = "[verified]" if report.tests_passed else "[unverified]"
                commit_msg = f"feat(continuum): implement task {task_id} {verified_tag}"
                subprocess.run(["git", "commit", "--no-verify", "-m", commit_msg], cwd=repo_path, check=True, capture_output=True)
        except Exception as git_err:
            logger.warning(f"Git commit error on branch {task_id}: {git_err}")

        return modified_files, report

    def synthesize_and_commit(self, repo_path: Path, prompt: str, task_id: str) -> List[str]:
        """
        Synthesizes code files for the prompt using Gemini Flash / SkyBrain, writes them into repo_path,
        and creates a git commit on the current task branch.
        Returns a list of created/modified file paths relative to repo_path.
        Raises RuntimeError if AI fails (Zero Fake Protocol).
        """
        files_to_write = self.ai_client.generate_code_files(prompt)
        
        if not files_to_write:
            raise RuntimeError(
                f"AI Code Synthesis failed for prompt: '{prompt}'. "
                "Neither Cloud Gemini Flash nor Local SkyBrain produced valid code files. "
                "Per Zero Fake Protocol, no fabricated placeholder files will be created."
            )

        modified_files = []
        for rel_path, content in files_to_write.items():
            full_path = repo_path / rel_path
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content, encoding="utf-8")
            modified_files.append(rel_path)

        if modified_files:
            try:
                subprocess.run(["git", "add", *modified_files], cwd=repo_path, check=True, capture_output=True)
                commit_msg = f"feat(continuum): implement task {task_id}"
                subprocess.run(["git", "commit", "--no-verify", "-m", commit_msg], cwd=repo_path, check=True, capture_output=True)
            except subprocess.CalledProcessError as e:
                err_msg = e.stderr.decode("utf-8", errors="ignore") if isinstance(e.stderr, bytes) else str(e.stderr)
                logger.error(f"Git commit failed during code synthesis: {err_msg}")
                raise RuntimeError(f"Git commit failed during code synthesis: {err_msg}")

        return modified_files

    def _generate_files(self, prompt: str, repo_path: Path) -> Dict[str, str]:
        """Queries SkyBrain for file modifications."""
        system_prompt = (
            "You are an expert autonomous software engineer working within an isolated sandbox. "
            "Given a user coding prompt, generate the required code files. "
            "You MUST respond ONLY with a valid JSON array of objects, where each object has: "
            '{"path": "relative/path/to/file.ext", "content": "file contents as a raw string"}. '
            "Do NOT include markdown formatting or explanations outside the JSON array."
        )

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2,
            "max_tokens": 1500
        }

        try:
            req = urllib.request.Request(
                self.skybrain_url,
                data=json.dumps(payload).encode("utf-8"),
                headers={"Content-Type": "application/json"}
            )
            with urllib.request.urlopen(req, timeout=30) as resp:
                data = json.loads(resp.read().decode("utf-8"))
                text = data["choices"][0]["message"]["content"]
                return self._parse_files_from_response(text, prompt)
        except Exception as e:
            logger.warning(f"SkyBrain call failed: {e}")
            return {}

    def _parse_files_from_response(self, text: str, prompt: str = "") -> Dict[str, str]:
        """Extracts files from LLM response (JSON array or code blocks)."""
        # 1. Try direct JSON parse
        clean_text = re.sub(r"^<think>.*?</think>", "", text, flags=re.DOTALL).strip()
        json_match = re.search(r"\[\s*\{.*\}\s*\]", clean_text, re.DOTALL)
        if json_match:
            try:
                items = json.loads(json_match.group(0))
                files = {}
                for it in items:
                    if isinstance(it, dict) and "path" in it and "content" in it:
                        files[it["path"]] = it["content"]
                if files:
                    return files
            except Exception:
                pass

        # Check if prompt specifies a filename like hello.py
        file_mention = re.search(r'\b([a-zA-Z0-9_\-]+\.(py|kt|java|md|json|sh|html|txt))\b', prompt)
        default_name = file_mention.group(1) if file_mention else None

        # 2. Try markdown code block extraction
        code_block_match = re.search(r"```([a-zA-Z0-9_\-]+)?\s*(?:#|//)?\s*(?:filename:)?\s*([a-zA-Z0-9_./\-]+)?\n(.*?)```", clean_text, re.DOTALL)
        if code_block_match:
            detected_path = code_block_match.group(2)
            lang = code_block_match.group(1) or "py"
            content = code_block_match.group(3)
            
            if not detected_path:
                if default_name:
                    detected_path = default_name
                else:
                    ext = "py" if "python" in lang or lang == "py" else ("kt" if lang in ("kt", "kotlin") else "txt")
                    detected_path = f"generated_code.{ext}"
            return {detected_path.strip(): content}

        if default_name and clean_text:
            return {default_name: clean_text}

        return {}
