"""Unit tests for Shadow Manager fallback backup engine."""
from pathlib import Path
from vibe_server.sandbox.shadow_manager import ShadowManager


def test_shadow_backup_and_restore(tmp_path: Path):
    workspace = tmp_path / "workspace"
    workspace.mkdir()
    
    # Create target config file
    config_file = workspace / "sample.conf"
    config_file.write_text("original_content=true", encoding="utf-8")
    
    manager = ShadowManager(workspace)
    
    # Backup
    backup_path = manager.backup_file(config_file)
    assert backup_path is not None
    assert backup_path.exists()
    assert "sample.conf.bak" in backup_path.name
    
    # Modify file
    config_file.write_text("corrupted_content=yes", encoding="utf-8")
    assert config_file.read_text(encoding="utf-8") == "corrupted_content=yes"
    
    # Restore
    restored = manager.restore_file(backup_path, config_file)
    assert restored is True
    assert config_file.read_text(encoding="utf-8") == "original_content=true"


def test_shadow_backup_nonexistent_returns_none(tmp_path: Path):
    manager = ShadowManager(tmp_path)
    non_existent = tmp_path / "does_not_exist.txt"
    assert manager.backup_file(non_existent) is None
