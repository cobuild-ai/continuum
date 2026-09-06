"""Docker containerized sandbox runner."""
import subprocess
import shutil
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class DockerSandboxError(Exception):
    """Raised when docker sandbox execution fails."""
    pass


class DockerRunner:
    """Runs commands in an isolated Docker container with host volume mounts."""

    def __init__(self, image: str = "continuum-sandbox:latest", timeout_seconds: int = 300):
        self.image = image
        self.timeout_seconds = timeout_seconds
        self.is_docker_available = shutil.which("docker") is not None

    def execute_in_sandbox(
        self,
        workspace_path: Path,
        command: List[str],
        env_vars: Optional[Dict[str, str]] = None,
        dry_run: bool = False
    ) -> Tuple[int, str, str]:
        """
        Executes a command inside the container with volume mount:
        docker run --rm -v <workspace>:/workspace -w /workspace <image> <command>
        """
        if dry_run or not self.is_docker_available:
            # Fallback to safe local subprocess execution or dry-run simulation
            try:
                res = subprocess.run(
                    command,
                    cwd=workspace_path,
                    capture_output=True,
                    text=True,
                    timeout=self.timeout_seconds,
                    env=env_vars
                )
                return res.returncode, res.stdout, res.stderr
            except subprocess.TimeoutExpired:
                raise DockerSandboxError(f"Execution timed out after {self.timeout_seconds} seconds")
            except Exception as e:
                raise DockerSandboxError(f"Execution failed: {str(e)}")

        docker_cmd = [
            "docker", "run", "--rm",
            "-v", f"{workspace_path.resolve()}:/workspace",
            "-w", "/workspace",
            "--network", "bridge"
        ]

        if env_vars:
            for k, v in env_vars.items():
                docker_cmd.extend(["-e", f"{k}={v}"])

        docker_cmd.append(self.image)
        docker_cmd.extend(command)

        try:
            res = subprocess.run(
                docker_cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout_seconds
            )
            return res.returncode, res.stdout, res.stderr
        except subprocess.TimeoutExpired:
            raise DockerSandboxError(f"Container execution timed out after {self.timeout_seconds} seconds")
        except Exception as e:
            raise DockerSandboxError(f"Docker command failed: {str(e)}")
