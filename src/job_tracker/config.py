from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "Job Application Tracker"
    database_url: str = "sqlite:///./job_tracker.db"
    auth_secret_key: str = "dev-only-change-this-secret-key"
    auth_algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")


settings = Settings()
