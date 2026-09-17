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
        smtp_use_tls=True,
    )
    mailer = SMTPActivationMailer(settings)
    await mailer.send_activation_link(email="user@example.com", code="abc-123")

    assert calls["hostname"] == "smtp.example.com"
    assert calls["port"] == 2525
    assert calls["use_tls"] is False
    assert calls["start_tls"] is True
    assert calls["message"]["To"] == "user@example.com"
    assert "http://example.test/activate?code=abc-123" in calls["message"].get_content()


async def test_smtp_mailer_uses_implicit_tls_on_port_465(monkeypatch: pytest.MonkeyPatch):
    calls = {}

    async def fake_send(message, *, hostname, port, username, password, use_tls, start_tls):
        calls["use_tls"] = use_tls
        calls["start_tls"] = start_tls

    monkeypatch.setattr("app.services.mailer.aiosmtplib.send", fake_send)

    settings = _settings(
        mailer_type=MailerType.SMTP,
        smtp_host="smtp.example.com",
        smtp_port=465,
        smtp_use_tls=False,
    )
    mailer = SMTPActivationMailer(settings)
    await mailer.send_activation_link(email="user@example.com", code="abc-123")

    # Port 465 is implicit-TLS (SMTPS) regardless of smtp_use_tls (which only
    # controls STARTTLS on other ports) — a plaintext connect to it just hangs.
    assert calls["use_tls"] is True
    assert calls["start_tls"] is False
