from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str

    @field_validator("database_url", mode="before")
    @classmethod
    def fix_database_url(cls, v: str) -> str:
        if v and v.startswith("postgresql://"):
            return v.replace("postgresql://", "postgresql+asyncpg://", 1)
        return v

    secret_key: str = "temporary_secret_key_for_build"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480

    first_treasurer_name: str = "Admin"
    first_treasurer_email: str = "admin@finor.local"
    first_treasurer_password: str = "change_this_password"


settings = Settings()
