from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file="../.env", extra="ignore")

    app_name: str = "EchoLoom"
    app_env: str = "development"
    app_secret: str = "change-me-to-a-long-random-secret"
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 1440
    llm_provider: str = "mock"
    audio_provider: str = "mock"
    pii_redaction_enabled: bool = True
    encryption_key: str = ""
    max_upload_mb: int = 50


@lru_cache
def get_settings() -> Settings:
    return Settings()
