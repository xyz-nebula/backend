from enum import Enum


class MailerType(str, Enum):
    """
    Which backend sends activation links.

    Attributes:
        SMTP: Sends real email via SMTP. Intended for production.
        LOG: Logs the link instead of sending it. Intended for local dev.
    """

    SMTP = "smtp"
    LOG = "log"


__all__ = ["MailerType"]
