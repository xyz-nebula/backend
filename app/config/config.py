from typing import Optional

from pydantic_settings import BaseSettings, SettingsConfigDict

from app.config.mailer_type import MailerType


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    refresh_token_expire_days: int = 30

    valkey_host: str = "localhost"
    valkey_port: int = 6379
    valkey_db: int = 0

    port: int = 3000
    debug: bool = False
    log_level: str = "INFO"
    db_url: str = "sqlite://db.sqlite3"

    activation_code_expire_minutes: int = 60
    activation_link_base_url: str = "http://localhost:5173/activate?code={code}"

    mailer_type: MailerType = MailerType.LOG
    smtp_host: Optional[str] = None
    smtp_port: int = 587
    smtp_user: Optional[str] = None
    smtp_password: Optional[str] = None
    smtp_from: str = "no-reply@nebula.local"
    smtp_use_tls: bool = True


settings = Settings()
