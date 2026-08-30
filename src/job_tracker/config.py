import secrets

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Job Application Tracker"
    database_url: str = "sqlite:///./job_tracker.db"
    # Generate an ephemeral secret when AUTH_SECRET_KEY is not supplied.
    # Production deployments should always provide a stable secret via the environment.
    auth_secret_key: str = Field(default_factory=lambda: secrets.token_urlsafe(48))
    auth_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")


settings = Settings()
