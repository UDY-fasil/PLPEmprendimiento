from pydantic_settings import BaseSettings, SettingsConfigDict
from functools import lru_cache


class Settings(BaseSettings):
    # App
    APP_NAME: str = "PLPE"
    APP_ENV: str = "development"
    DEBUG: bool = True

    # URLs completas (vienen del docker-compose.yml o .env)
    MARIADB_URL: str
    MONGODB_URL: str

    # JWT
    SECRET_KEY: str = "cambia_esto_en_produccion"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # Seguridad
    ARGON2_TIME_COST: int = 3
    ARGON2_MEMORY_COST: int = 65536
    ARGON2_PARALLELISM: int = 4

    # TOTP
    TOTP_ISSUER: str = "PLPE"

    # Rate limiting
    LOGIN_MAX_ATTEMPTS: int = 5
    LOGIN_BLOCK_MINUTES: int = 15

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()