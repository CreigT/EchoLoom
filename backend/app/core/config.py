from functools import lru_cache
from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")

    app_name: str = "EchoLoom"
    app_env: str = "development"
    app_secret: str = "change-me-to-a-long-random-secret"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    public_base_url: str = "http://localhost:8000"
    allowed_origins: str = "*"
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440
    llm_provider: str = "mock"
    audio_provider: str = "mock"
    pii_redaction_enabled: bool = True
    encryption_key: str = ""
    max_upload_mb: int = 50
    data_dir: str = "../data"
    persist_enabled: bool = True
    rate_limit_per_minute: int = 60
    require_voice_consent: bool = True

    def data_path(self) -> Path:
        path = Path(self.data_dir)
        path.mkdir(parents=True, exist_ok=True)
        return path

    def is_production(self) -> bool:
        return self.app_env.lower() in {"production", "prod"}

    def origin_list(self) -> list[str]:
        raw = self.allowed_origins.strip()
        if raw == "*":
            return ["*"]
        return [item.strip() for item in raw.split(",") if item.strip()]

    def assert_deploy_safe(self) -> None:
        if not self.is_production():
            return
        if self.app_secret == "change-me-to-a-long-random-secret" or len(self.app_secret) < 24:
            raise RuntimeError("Set APP_SECRET to a long random value before production deploy")


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    settings.assert_deploy_safe()
    return settings
