from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "MMS Express"
    APP_ENV: str = "development"
    DEBUG: bool = True

    DATABASE_URL: str = "postgresql+asyncpg://mms_user:mms_password@localhost:5432/mms_express"
    REDIS_URL: str = "redis://localhost:6379/0"

    SECRET_KEY: str = "change-me-to-a-random-64-char-string"
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    CORS_ORIGINS: str = "http://localhost:3000,http://localhost:8081"

    FIRST_ADMIN_EMAIL: str = "admin@mmsexpress.com"
    FIRST_ADMIN_PASSWORD: str = "Admin123!"

    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "mistral"

    GPS_UPDATE_INTERVAL_SECONDS: int = 10
    GPS_MAX_HISTORY_DAYS: int = 30

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",")]

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
