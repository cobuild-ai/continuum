"""Server configuration settings."""
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="CONTINUUM_", env_file=".env", extra="ignore")

    app_name: str = "Continuum Vibe Server"
    host: str = "0.0.0.0"
    port: int = 8080
    debug: bool = False
    
    # Workspace & Git (01-production scoped anchor)
    default_workspace_root: Path = Path("/Users/smilelife/Projects/OSSProject/01-production")
    ai_branch_prefix: str = "ai/"
    
    # Sandbox
    docker_image: str = "continuum-sandbox:latest"
    sandbox_timeout_seconds: int = 300
    
    # AI Engine (Hybrid Routing: Gemini Flash & SkyBrain SLM)
    ai_provider: str = "gemini"  # "gemini" or "skybrain"
    gemini_model: str = "gemini-3.8-flash"
    gemini_api_key: str = ""
    skybrain_url: str = "http://127.0.0.1:8000/v1/chat/completions"
    skybrain_model: str = "qwen3.8"

    # Notification
    fcm_enabled: bool = False
    fcm_service_account_path: str = ""
    fcm_target_token: str = ""


settings = Settings()
