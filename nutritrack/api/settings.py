from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import SecretStr
from functools import lru_cache


class Settings(BaseSettings):
    # Secrets: SecretStr hides them when printed or logged.
    # Read the real value with .get_secret_value().
    database_url: SecretStr = SecretStr("")  # contains the database password
    secret_key: SecretStr = SecretStr("changeme-in-production")
    session_secret_key: SecretStr = SecretStr("")
    anthropic_api_key: SecretStr = SecretStr("")
    voyage_api_key: SecretStr = SecretStr("")
    resend_api_key: SecretStr = SecretStr("")
    google_client_secret: SecretStr = SecretStr("")
    # mail_password: SecretStr = SecretStr("")

    # Not secret
    access_token_expire_minutes: int = 60 * 24 * 7
    environment: str = "development"
    redis_url: str = "redis://localhost:6379/0"
    mail_username: str = ""
    mail_from: str = ""
    allowed_origins: str = "http://localhost:5173"
    google_client_id: str = ""
    google_redirect_uri: str = "http://localhost:8000/auth/google/callback"
    frontend_url: str = "http://localhost:5173"

    model_config = SettingsConfigDict(env_file=".env", hide_input_in_errors=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()
