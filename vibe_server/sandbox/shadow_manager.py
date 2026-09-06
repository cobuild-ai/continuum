"""Shadow Manager: Fallback backup engine for host configuration changes."""
import os
import shutil
import time
from pathlib import Path
from typing import Optional


class ShadowManager:
    """Safely creates and restores backups under .external_shadow for out-of-sandbox mutations."""

    def __init__(self, workspace_root: Path):
        self.workspace_root = workspace_root
        self.shadow_dir = workspace_root / ".external_shadow"

    def backup_file(self, target_path: Path) -> Optional[Path]:
        """Backs up an external target file with timestamp prefix."""
        if not target_path.exists():
            return None

        self.shadow_dir.mkdir(parents=True, exist_ok=True)
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        backup_name = f"{timestamp}_{target_path.name}.bak"
        backup_path = self.shadow_dir / backup_name

        shutil.copy2(target_path, backup_path)
        return backup_path

    def restore_file(self, backup_path: Path, target_path: Path) -> bool:
        """Restores an external file from its shadow backup."""
        if not backup_path.exists():
            return False
        shutil.copy2(backup_path, target_path)
        return True
