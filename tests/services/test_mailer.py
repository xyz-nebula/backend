import logging

import pytest

from app.config.config import Settings
from app.config.mailer_type import MailerType
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

    async def fake_send(message, *, hostname, port, username, password, start_tls):
        calls["message"] = message
        calls["hostname"] = hostname
        calls["port"] = port

    monkeypatch.setattr("app.services.mailer.aiosmtplib.send", fake_send)

    settings = _settings(
        mailer_type=MailerType.SMTP,
        smtp_host="smtp.example.com",
        smtp_port=2525,
    )
    mailer = SMTPActivationMailer(settings)
    await mailer.send_activation_link(email="user@example.com", code="abc-123")

    assert calls["hostname"] == "smtp.example.com"
    assert calls["port"] == 2525
    assert calls["message"]["To"] == "user@example.com"
    assert "http://example.test/activate?code=abc-123" in calls["message"].get_content()
