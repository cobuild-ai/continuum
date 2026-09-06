"""Server configuration settings."""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CONTINUUM_", env_file=".env", extra="ignore")

    app_name: str = "Continuum Vibe Server"
    host: str = "0.0.0.0"
    port: int = 8080
    debug: bool = False
    
    # Workspace & Git
    default_workspace_root: Path = Path("/Users/smilelife/Projects/OSSProject")
    ai_branch_prefix: str = "ai/"
    
    # Sandbox
    docker_image: str = "continuum-sandbox:latest"
    sandbox_timeout_seconds: int = 300
    
    # Notification
    fcm_enabled: bool = False
    fcm_service_account_path: str = ""
    fcm_target_token: str = ""


settings = Settings()
