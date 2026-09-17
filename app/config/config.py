from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    
    valkey_host: str = "localhost"
    valkey_port: int = 6379
    valkey_db: int = 0

    debug: bool = False
    log_level: str = "INFO"
    db_url: str = "sqlite://db.sqlite3"



settings = Settings()
