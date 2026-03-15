from pydantic_settings import BaseSettings, SettingsConfigDict
import os
from functools import cache


class Settings(BaseSettings):
    database_url: str
    celery_broker_url: str
    celery_result_backend: str
    binance_url: str

    model_config = SettingsConfigDict(
        env_file=os.getenv("ENV_FILE", ".env"),
        extra="ignore"
    )

@cache
def get_settings():
    return Settings()

settings = get_settings()
