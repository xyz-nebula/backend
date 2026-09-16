from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    jwt_access_token_expire_minutes: int = 15
    jwt_refresh_token_expire_minutes: int = 60 * 24 * 7
    
    valkey_host: str = "localhost"
    valkey_port: int = 6379
    valkey_db: int = 0


settings = Settings()
