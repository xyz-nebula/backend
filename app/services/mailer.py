import logging
from abc import ABC, abstractmethod

import aiosmtplib
from email.message import EmailMessage

from app.config.config import Settings, settings
from app.config.mailer_type import MailerType

logger = logging.getLogger(__name__)


class ActivationMailer(ABC):
    @abstractmethod
    async def send_activation_link(self, *, email: str, code: str) -> None: ...


class LogActivationMailer(ActivationMailer):
    """Logs the activation link instead of sending it. Used in dev."""

    def __init__(self, config: Settings):
        self._config = config

    async def send_activation_link(self, *, email: str, code: str) -> None:
        link = self._config.activation_link_base_url.format(code=code)
        logger.info("Activation link for %s: %s", email, link)


class SMTPActivationMailer(ActivationMailer):
    """Sends the activation link by email via SMTP. Used in production."""

    def __init__(self, config: Settings):
        self._config = config

    async def send_activation_link(self, *, email: str, code: str) -> None:
        link = self._config.activation_link_base_url.format(code=code)

        message = EmailMessage()
        message["From"] = self._config.smtp_from
        message["To"] = email
        message["Subject"] = "Confirm your Nebula account"
        message.set_content(
            f"Activate your account by opening the following link:\n\n{link}\n\n"
            "If you didn't request this, you can ignore this email."
        )

        # Port 465 is implicit TLS (SMTPS) — the server expects a TLS handshake
        # immediately, not a plaintext greeting, so it needs aiosmtplib's use_tls=
        # rather than start_tls= (the STARTTLS-upgrade mode used on e.g. port 587).
        implicit_tls = self._config.smtp_port == 465

        await aiosmtplib.send(
            message,
            hostname=self._config.smtp_host,
            port=self._config.smtp_port,
            username=self._config.smtp_user,
            password=self._config.smtp_password,
            use_tls=implicit_tls,
            start_tls=False if implicit_tls else self._config.smtp_use_tls,
        )


class MailerFactory:
    @staticmethod
    def create(config: Settings) -> ActivationMailer:
        if config.mailer_type == MailerType.SMTP:
            return SMTPActivationMailer(config)
        if config.mailer_type == MailerType.LOG:
            return LogActivationMailer(config)
        raise ValueError(f"Unknown mailer type: {config.mailer_type}")


def get_activation_mailer() -> ActivationMailer:
    return MailerFactory.create(settings)


__all__ = [
    "ActivationMailer",
    "LogActivationMailer",
    "SMTPActivationMailer",
    "MailerFactory",
    "get_activation_mailer",
]
