from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    database_url: str
    secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 480

    first_treasurer_name: str = "Admin"
    first_treasurer_email: str = "admin@finor.local"
    first_treasurer_password: str = "change_this_password"


settings = Settings()
