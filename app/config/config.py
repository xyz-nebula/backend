import logging

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.config.mailer_type import MailerType
from app.config.smtp_tls_mode import SmtpTlsMode

logger = logging.getLogger(__name__)

DEFAULT_ADMIN_CODE = "change-me"


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60
    refresh_token_expire_days: int = 30
    admin_code: str = DEFAULT_ADMIN_CODE

    valkey_host: str = "localhost"
    valkey_port: int = 6379
    valkey_db: int = 0

    port: int = 3000
    root_path: str = "/"
    debug: bool = False
    log_level: str = "INFO"
    db_url: str = "sqlite://db.sqlite3"

    activation_code_expire_minutes: int = 60
    activation_link_base_url: str = "http://example.com/activate?code={code}"

    mailer_type: MailerType = MailerType.LOG
    smtp_host: str | None = None
    smtp_port: int = 587
    smtp_user: str | None = None
    smtp_password: str | None = None
    smtp_from: str = "no-reply@nebula.local"
    smtp_tls_mode: SmtpTlsMode = SmtpTlsMode.STARTTLS

    @model_validator(mode="after")
    def warn_on_default_admin_code(self) -> Settings:
        if self.admin_code == DEFAULT_ADMIN_CODE:
            logger.warning(
                "ADMIN_CODE is still the default '%s' — set a strong value in .env",
                DEFAULT_ADMIN_CODE,
            )
        return self


settings = Settings()
