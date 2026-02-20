from __future__ import annotations

from functools import lru_cache

from pydantic_settings import (
    BaseSettings,
    DotEnvSettingsSource,
    EnvSettingsSource,
    PydanticBaseSettingsSource,
    SettingsConfigDict,
)


class Settings(BaseSettings):
    openai_api_key: str
    openai_base_url: str = ""   # leave blank for OpenAI; set to Groq/Gemini URL for free providers
    model_id: str = "gpt-4o"
    db_path: str = "sessions.db"
    # CORS origin(s) for the React dev server; comma-separated
    cors_origins: str = "http://localhost:5173,http://localhost:5174,http://localhost:3000"

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    @classmethod
    def settings_customise_sources(
        cls,
        settings_cls: type[BaseSettings],
        init_settings: PydanticBaseSettingsSource,
        env_settings: EnvSettingsSource,
        dotenv_settings: DotEnvSettingsSource,
        **kwargs: PydanticBaseSettingsSource,
    ) -> tuple[PydanticBaseSettingsSource, ...]:
        # .env file takes priority over system environment variables.
        # This prevents a stale system OPENAI_API_KEY from shadowing the .env value.
        return init_settings, dotenv_settings, env_settings

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()  # type: ignore[call-arg]
