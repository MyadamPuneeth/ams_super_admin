import asyncio
import smtplib
import ssl
from unittest.mock import MagicMock

import pytest

from ams_api.mail import Mailer


@pytest.mark.parametrize("security,port", [("starttls", "587"), ("ssl", "465"), ("none", "25")])
def test_smtp_credentials_delivery(monkeypatch, security, port):
    for key, value in {
        "SMTP_HOST": "smtp.gmail.com", "SMTP_PORT": port, "SMTP_SECURITY": security,
        "SMTP_USERNAME": "sender@example.test", "SMTP_PASSWORD": "test-app-password",
        "SMTP_FROM": "", "USER_APP_ORIGIN": "https://academy.example.test",
    }.items():
        monkeypatch.setenv(key, value)
    smtp = MagicMock()
    smtp_ssl = MagicMock()
    monkeypatch.setattr(smtplib, "SMTP", smtp)
    monkeypatch.setattr(smtplib, "SMTP_SSL", smtp_ssl)
    asyncio.run(Mailer().send_credentials("admin@example.test", "Test Academy", "academy.admin", "temporary-pass"))
    factory = smtp_ssl if security == "ssl" else smtp
    (smtp if security == "ssl" else smtp_ssl).assert_not_called()
    assert factory.call_args.args == ("smtp.gmail.com", int(port))
    assert factory.call_args.kwargs["timeout"] == 15
    client = factory.return_value.__enter__.return_value
    if security != "none":
        context = factory.call_args.kwargs["context"] if security == "ssl" else client.starttls.call_args.kwargs["context"]
        assert context.verify_mode == ssl.CERT_REQUIRED and context.check_hostname
    if security != "starttls": client.starttls.assert_not_called()
    client.login.assert_called_once_with("sender@example.test", "test-app-password")
    message = client.send_message.call_args.args[0]
    assert message["From"] == "sender@example.test" and message["To"] == "admin@example.test"
    assert message["Subject"] == "Your Test Academy administrator account"
    assert all(value in message.get_content() for value in ("academy.admin", "temporary-pass", "https://academy.example.test"))
    if security == "starttls":
        assert [call[0] for call in client.method_calls] == ["starttls", "login", "send_message"]
    client.send_message.side_effect = smtplib.SMTPAuthenticationError(535, b"Authentication failed")
    with pytest.raises(smtplib.SMTPAuthenticationError):
        asyncio.run(Mailer().send_credentials("admin@example.test", "Test Academy", "academy.admin", "temporary-pass"))


def test_missing_smtp_configuration(monkeypatch):
    monkeypatch.setenv("NODE_ENV", "test")
    monkeypatch.setenv("SMTP_HOST", "smtp.gmail.com")
    monkeypatch.setenv("SMTP_FROM", "")
    monkeypatch.setenv("SMTP_USERNAME", "")
    monkeypatch.setenv("SMTP_PASSWORD", "")
    smtp = MagicMock()
    monkeypatch.setattr(smtplib, "SMTP", smtp)
    with pytest.raises(RuntimeError, match="SMTP is not configured"):
        asyncio.run(Mailer().send_credentials("admin@example.test", "Academy", "admin", "temporary-pass"))
    monkeypatch.setenv("SMTP_USERNAME", "sender@example.test")
    with pytest.raises(RuntimeError, match="Google app password"):
        asyncio.run(Mailer().send_credentials("admin@example.test", "Academy", "admin", "temporary-pass"))
    smtp.assert_not_called()
