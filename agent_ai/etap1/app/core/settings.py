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
    openai_model: str = "gpt-5.4-mini"
    ai_max_input_chars: int = 1200
    ai_max_output_tokens: int = 300
    ai_daily_request_limit: int = 50

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