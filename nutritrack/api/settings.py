from pydantic_settings import BaseSettings
from functools import lru_cache


class Settings(BaseSettings):
    database_url: str = ""
    secret_key: str = "changeme-in-production"
    access_token_expire_minutes: int = 60 * 24
    environment: str = "development"
    anthropic_api_key: str = ""
    redis_url: str = "redis://localhost:6379/0"
    mail_username: str = ""
    mail_password: str = ""
    mail_from: str = ""
    resend_api_key: str = ""

    model_config = {"env_file": ".env"}


@lru_cache
def get_settings() -> Settings:
    return Settings()
