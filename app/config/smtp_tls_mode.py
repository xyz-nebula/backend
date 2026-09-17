from enum import Enum


class SmtpTlsMode(str, Enum):
    """
    How the SMTP mailer secures its connection.

    Attributes:
        NONE: No TLS at all (plaintext).
        STARTTLS: Plaintext connect, then upgrade via STARTTLS (e.g. port 587).
        TLS: Implicit TLS from the first byte (SMTPS, e.g. port 465).
    """

    NONE = "none"
    STARTTLS = "starttls"
    TLS = "tls"


__all__ = ["SmtpTlsMode"]
