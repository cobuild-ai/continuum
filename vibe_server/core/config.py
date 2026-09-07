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
    
    # AI Engine Settings (Controlled via .env without code modifications)
    # Available providers: "gemini" | "claude" | "codex" | "openai" | "skybrain"
    ai_provider: str = "gemini"
    
    # Gemini Configuration
    gemini_model: str = "gemini-3.8-flash"
    gemini_api_key: str = ""

    # Claude Configuration
    claude_model: str = "claude-3-7-sonnet-20250219"
    claude_api_key: str = ""

    # OpenAI / Codex Configuration
    openai_model: str = "gpt-4o"
    openai_api_key: str = ""

    # Local SkyBrain SLM (Optional: set to False if SkyBrain daemon is not running)
    skybrain_enabled: bool = False
    skybrain_url: str = "http://127.0.0.1:8000/v1/chat/completions"
    skybrain_model: str = "qwen3.8"

    @property
    def active_model_name(self) -> str:
        if self.ai_provider == "gemini":
            return self.gemini_model
        elif self.ai_provider == "claude":
            return self.claude_model
        elif self.ai_provider in ("codex", "openai"):
            return self.openai_model
        elif self.ai_provider == "skybrain":
            return self.skybrain_model
        return self.gemini_model

    # Notification
    fcm_enabled: bool = False
    fcm_service_account_path: str = ""
    fcm_target_token: str = ""


settings = Settings()
