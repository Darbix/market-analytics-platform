from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    market_api_url: str

    class Config:
        env_file = ".env"
        extra = "ignore"

settings = Settings()
