import logging

import pytest

from app.config.config import Settings
from app.config.mailer_type import MailerType
from app.config.smtp_tls_mode import SmtpTlsMode
from app.services.mailer import LogActivationMailer, MailerFactory, SMTPActivationMailer


def _settings(**overrides) -> Settings:
    return Settings(
        activation_link_base_url="http://example.test/activate?code={code}",
        **overrides,
    )


async def test_log_mailer_logs_link(caplog: pytest.LogCaptureFixture):
    mailer = LogActivationMailer(_settings())
    with caplog.at_level(logging.INFO):
        await mailer.send_activation_link(email="user@example.com", code="abc-123")

    assert "http://example.test/activate?code=abc-123" in caplog.text
    assert "user@example.com" in caplog.text


def test_factory_picks_log_mailer():
    mailer = MailerFactory.create(_settings(mailer_type=MailerType.LOG))
    assert isinstance(mailer, LogActivationMailer)


def test_factory_picks_smtp_mailer():
    mailer = MailerFactory.create(_settings(mailer_type=MailerType.SMTP))
    assert isinstance(mailer, SMTPActivationMailer)


async def test_smtp_mailer_sends_via_aiosmtplib(monkeypatch: pytest.MonkeyPatch):
    calls = {}

    async def fake_send(message, *, hostname, port, username, password, use_tls, start_tls):
        calls["message"] = message
        calls["hostname"] = hostname
        calls["port"] = port
        calls["use_tls"] = use_tls
        calls["start_tls"] = start_tls

    monkeypatch.setattr("app.services.mailer.aiosmtplib.send", fake_send)

    settings = _settings(
        mailer_type=MailerType.SMTP,
        smtp_host="smtp.example.com",
        smtp_port=2525,
        smtp_tls_mode=SmtpTlsMode.STARTTLS,
    )
    mailer = SMTPActivationMailer(settings)
    await mailer.send_activation_link(email="user@example.com", code="abc-123")

    assert calls["hostname"] == "smtp.example.com"
    assert calls["port"] == 2525
    assert calls["use_tls"] is False
    assert calls["start_tls"] is True
    assert calls["message"]["To"] == "user@example.com"
    assert "http://example.test/activate?code=abc-123" in calls["message"].get_content()


@pytest.mark.parametrize(
    ("mode", "expected_use_tls", "expected_start_tls"),
    [
        (SmtpTlsMode.TLS, True, False),
        (SmtpTlsMode.STARTTLS, False, True),
        (SmtpTlsMode.NONE, False, False),
    ],
)
async def test_smtp_mailer_tls_mode_is_explicit(
    monkeypatch: pytest.MonkeyPatch, mode, expected_use_tls, expected_start_tls
):
    calls = {}

    async def fake_send(message, *, hostname, port, username, password, use_tls, start_tls):
        calls["use_tls"] = use_tls
        calls["start_tls"] = start_tls

    monkeypatch.setattr("app.services.mailer.aiosmtplib.send", fake_send)

    settings = _settings(
        mailer_type=MailerType.SMTP,
        smtp_host="smtp.example.com",
        # A deliberately "wrong" port for the mode, to prove this is driven by
        # smtp_tls_mode alone and not inferred from the port.
        smtp_port=2525,
        smtp_tls_mode=mode,
    )
    mailer = SMTPActivationMailer(settings)
    await mailer.send_activation_link(email="user@example.com", code="abc-123")

    assert calls["use_tls"] is expected_use_tls
    assert calls["start_tls"] is expected_start_tls
