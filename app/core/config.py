from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class AppSettings(BaseSettings):
	environment: str = "dev"
	db_conn_url: str = "sqlite:///./books.db"

	# .ENV
	model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")


@lru_cache
def get_app_settings() -> AppSettings:
	return AppSettings()
