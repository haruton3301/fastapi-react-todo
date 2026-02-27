from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    cors_origins: str
    secret_key: str
    access_token_expire_minutes: int = 30
    refresh_token_expire_days: int = 7
    cookie_secure: bool = False
    smtp_host: str = "mailpit"
    smtp_port: int = 1025
    smtp_from: str = "noreply@example.com"
    frontend_url: str = "http://localhost:3000"
    password_reset_token_expire_minutes: int = 60

    @property
    def cors_origins_list(self) -> list[str]:
        return [origin.strip() for origin in self.cors_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()
