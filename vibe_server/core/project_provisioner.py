"""Project provisioner: Ensures strict Git sovereignty, automatic repository initialization, and tailored .gitignore provisioning."""
import logging
import subprocess
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

GITIGNORE_PYTHON = """# Python
__pycache__/
*.py[cod]
*$py.class
*.so
.Python
build/
develop-eggs/
dist/
downloads/
eggs/
.eggs/
lib/
lib64/
parts/
sdist/
var/
wheels/
*.egg-info/
.installed.cfg
*.egg
.env
.venv
venv/
ENV/
.pytest_cache/
.coverage
htmlcov/
.mypy_cache/
.ruff_cache/
.DS_Store
"""

GITIGNORE_ANDROID = """# Android & Gradle
.gradle/
build/
app/build/
*.apk
*.aab
*.ap_
local.properties
.idea/
*.iml
captures/
.externalNativeBuild/
.cxx/
.DS_Store
"""

GITIGNORE_NODE = """# Node
node_modules/
npm-debug.log*
yarn-debug.log*
yarn-error.log*
dist/
build/
.env
.env.local
.DS_Store
"""

GITIGNORE_DEFAULT = """# Default Continuum Workspace
.DS_Store
Thumbs.db
*.log
tmp/
temp/
.external_shadow/
.venv/
build/
dist/
"""


class ProjectProvisioner:
    """Manages single-project Git lifecycle and automated environment provisioning."""

    @staticmethod
    def detect_tech_stack(project_path: Path) -> str:
        """Heuristically detects project tech stack based on marker files."""
        if any((project_path / f).exists() for f in ["build.gradle", "build.gradle.kts", "settings.gradle.kts", "AndroidManifest.xml"]):
            return "android"
        if any((project_path / f).exists() for f in ["pyproject.toml", "requirements.txt", "setup.py", "Pipfile"]):
            return "python"
        if any((project_path / f).exists() for f in ["package.json", "yarn.lock", "pnpm-lock.yaml"]):
            return "node"
        
        # Check files inside project
        py_files = list(project_path.glob("*.py"))
        if py_files:
            return "python"
        kt_files = list(project_path.glob("*.kt"))
        if kt_files:
            return "android"
        js_files = list(project_path.glob("*.js")) or list(project_path.glob("*.ts"))
        if js_files:
            return "node"

        return "default"

    @classmethod
    def get_gitignore_template(cls, tech_stack: str) -> str:
        if tech_stack == "android":
            return GITIGNORE_ANDROID
        elif tech_stack == "python":
            return GITIGNORE_PYTHON
        elif tech_stack == "node":
            return GITIGNORE_NODE
        return GITIGNORE_DEFAULT

    @classmethod
    def ensure_git_repository(
        cls,
        project_path: Path,
        author_name: str = "Continuum Maintainer",
        author_email: str = "maintainer@continuum.ai"
    ) -> bool:
        """
        Ensures the given directory is an active, clean Git repository.
        If .git is missing:
        1. Runs `git init -b main`
        2. Configures default user.name and user.email if missing
        3. Creates a tailored .gitignore if not present
        4. Creates a baseline README.md if not present
        5. Commits baseline files
        """
        project_path.mkdir(parents=True, exist_ok=True)
        git_dir = project_path / ".git"
        is_new_repo = not git_dir.exists()

        if is_new_repo:
            logger.info(f"Initializing new Git repository at: {project_path}")
            res = subprocess.run(["git", "init", "-b", "main"], cwd=project_path, capture_output=True, text=True)
            if res.returncode != 0:
                logger.error(f"git init failed: {res.stderr}")
                return False

            # Ensure local git identity exists for commits
            subprocess.run(["git", "config", "user.name", author_name], cwd=project_path, capture_output=True)
            subprocess.run(["git", "config", "user.email", author_email], cwd=project_path, capture_output=True)

        # 2. Ensure .gitignore
        gitignore_path = project_path / ".gitignore"
        if not gitignore_path.exists():
            tech_stack = cls.detect_tech_stack(project_path)
            content = cls.get_gitignore_template(tech_stack)
            gitignore_path.write_text(content, encoding="utf-8")
            logger.info(f"Provisioned {tech_stack} .gitignore for {project_path.name}")

        # 3. Ensure README.md if folder is completely empty
        readme_path = project_path / "README.md"
        if not readme_path.exists() and len(list(project_path.iterdir())) <= 2:
            readme_content = f"# {project_path.name}\n\nManaged by Continuum Vibe Coding & Git Sovereignty Orchestrator.\n"
            readme_path.write_text(readme_content, encoding="utf-8")

        # 4. If newly initialized, create initial commit
        if is_new_repo:
            try:
                subprocess.run(["git", "add", "."], cwd=project_path, check=True, capture_output=True)
                status_res = subprocess.run(["git", "status", "--porcelain"], cwd=project_path, capture_output=True, text=True)
                if status_res.stdout.strip():
                    subprocess.run(
                        ["git", "commit", "--no-verify", "-m", "chore: initialize repository with .gitignore (Continuum)"],
                        cwd=project_path,
                        check=True,
                        capture_output=True
                    )
            except Exception as e:
                logger.warning(f"Initial commit during provision failed: {e}")

        return True
