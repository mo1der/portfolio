import os

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # --- podstawowe informacje o aplikacji ---
    app_name: str = "AI Classifier Backend"
    app_version: str = "1.5.0"

    # --- środowisko: development, production, test ---
    environment: str = "development"

    # --- AI ---
    ai_enabled: bool = True
    openai_api_key: str | None = None
    openai_model: str = "gpt-4o-mini"

    # --- Baza danych ---
    database_url: str = "sqlite:///./ai_classifier.db"

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


# --- automatyczne przełączenie pliku konfiguracyjnego ---
env_file = ".env.test" if os.environ.get("ENVIRONMENT") == "test" else ".env"

settings = Settings(_env_file=env_file)