from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    SECRET_KEY: str = "change-this-in-dev"
    ALGORITHM: str = "HS256"

    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    TEST_DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost/test_db"
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@db:5432/app_db"
    SENTRY_DNS: str = "https://abc123@o123456.ingest.sentry.io/987654"
    APP_ENV: str = "development"
    SQL_ECHO: bool = False

    class Config:
        env_file = ".env"


settings = Settings()
