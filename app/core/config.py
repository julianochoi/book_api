from functools import lru_cache

from pydantic import SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
	environment: str = "dev"
	database_url: str = "sqlite+aiosqlite:///./books.db"
	redis_url: str = "redis://redis:6379"

	# JWT
	jwt_secret: SecretStr
	jwt_expire_minutes: int = 30

	# .ENV
	model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_app_settings() -> AppSettings:
	return AppSettings()  # type: ignore[call-arg]
