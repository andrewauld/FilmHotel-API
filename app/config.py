"""
Centralised application configuration.

Reads settings from environment variables / .env file using pydantic-settings.
"""

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Application settings — all values can be overridden via environment variables."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
    )

    # ── Database ──────────────────────────────────────
    database_url: str = "postgresql://postgres:password@localhost:5432/filmhotel"

    # ── JWT Authentication ────────────────────────────
    secret_key: str = "change-me-to-a-random-secret"
    access_token_expire_minutes: int = 60
    algorithm: str = "HS256"

    # ── TMDB API ──────────────────────────────────────
    tmdb_api_key: str = ""
    tmdb_base_url: str = "https://api.themoviedb.org/3"

    # ── Google Gemini AI ──────────────────────────────
    gemini_api_key: str = ""
    gemini_model: str = "gemini-2.0-flash"

    # ── App metadata ──────────────────────────────────
    app_name: str = "FilmHotel API"
    app_version: str = "1.0.0"
    debug: bool = False


settings = Settings()
