from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    api_secret: str
    jwt_secret: str
    jwt_valid_seconds: int
    sqlite_filename: str
    image_dir: str = "static/image/photo/"
    file_dir: str = "static/download/"
    file_max_size: int = 10000000
    article_dir: str = "static/article/"
    user_check: bool = True
    enrollment_fee: int = 25000
    cors_all_accept: bool = False
    rabbitmq_host: str = "rabbitmq"
    bot_host: str = "bot"
    discord_receive_queue: str = "discord_bot_queue"
    rabbitmq_required: bool = True
    enable_test_routes: bool = False
    notice_channel_id: int
    grant_channel_id: int
    w_html_dir: str = "static/w/"

    model_config = SettingsConfigDict(env_file=".env", frozen=True)


@lru_cache
def get_settings() -> Settings:
    return Settings()  # type: ignore
