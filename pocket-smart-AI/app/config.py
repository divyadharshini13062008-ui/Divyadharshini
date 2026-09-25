from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "PocketSmart AI"
    environment: str = "development"

    secret_key: str = "change-this-secret-key"

    database_url: str = "sqlite:///./data/pocketsmart.db"

    access_token_expire_minutes: int = 120

    gemini_api_key: str | None = None
    gemini_model: str = "gemini-3.8-flash"

    use_mock_ai: bool = True

    max_image_mb: int = 5

    cors_origins: str = (
        "http://127.0.0.1:8000,"
        "http://localhost:8000"
    )

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    @property
    def cors_origin_list(self) -> list[str]:
        return [
            origin.strip()
            for origin in self.cors_origins.split(",")
            if origin.strip()
        ]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()