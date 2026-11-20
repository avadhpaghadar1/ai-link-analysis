from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    bluesky_identifier: str | None = None
    bluesky_app_password: str | None = None
    mastodon_base_url: str = "https://mastodon.social"
    mastodon_access_token: str | None = None
    reddit_client_id: str | None = None
    reddit_client_secret: str | None = None
    reddit_username: str | None = None
    reddit_password: str | None = None
    reddit_subreddit: str | None = None
    dev_api_key: str | None = None
    linkedin_access_token: str | None = None
    linkedin_author_urn: str | None = None
    request_timeout_seconds: float = 20.0


@lru_cache
def get_settings() -> Settings:
    return Settings()
