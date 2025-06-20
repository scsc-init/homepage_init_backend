from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_secret: str
    jwt_secret: str
    jwt_valid_seconds: int
    sqlite_filename: str
    image_dir: str
    image_max_size: int
    file_dir: str
    file_max_size: int
    article_dir: str
    user_check: bool
    enrollment_fee: int
    cors_all_accept: bool

    model_config = SettingsConfigDict(env_file=".env", frozen=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore
