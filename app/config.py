from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # Application
    app_env: str = "development"
    secret_key: str
    access_token_expire_minutes: int = 30

    # Database
    database_url: str

    # Webhook
    webhook_timeout_seconds: int = 10
    webhook_max_retries: int = 3
    webhook_retry_delay_seconds: int = 60

    @property
    def is_production(self) -> bool:
        return self.app_env.lower() == "production"

    @property
    def sqlalchemy_database_url(self) -> str:
        """
        Railway injects DATABASE_URL as postgres:// (legacy format).
        SQLAlchemy requires postgresql+psycopg2://.
        This property normalizes both cases.
        """
        url = self.database_url
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql://", 1)
        return url


settings = Settings()
