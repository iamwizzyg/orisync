from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application settings loaded from environment variables.
    All values come from the .env file in development.
    In production, set these as real environment variables.
    """

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


# Single instance imported everywhere else in the app
settings = Settings()
