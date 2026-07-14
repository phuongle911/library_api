from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    SECRET_KEY: str = "8d4f2a9c7e1b5f6a3d8c0e4f9b7a2c1d5e8f3a6b9c2d7e1f4a8b5c0d9e2f6a1b"
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
