from pydantic_settings import BaseSettings, SettingsConfigDict
import os

ENV = os.getenv("ENV", "local")

class AuthSettings(BaseSettings):
    ACCESS_TOKEN_SECRET: str
    REFRESH_TOKEN_SECRET: str
    SHORT_SESSION_LIFESPAN: int = 15
    LONG_SESSION_LIFESPAN: int = 24 * 60

    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=f".env.{ENV}",
        extra='ignore'
    )

AUTH_SETTINGS = AuthSettings()