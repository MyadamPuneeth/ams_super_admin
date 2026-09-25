import asyncio
import os
import smtplib
from email.message import EmailMessage

class Mailer:
    def __init__(self) -> None:
        self.host = os.getenv("SMTP_HOST", "")
        self.port = int(os.getenv("SMTP_PORT", "587"))
        self.security = os.getenv("SMTP_SECURITY", "starttls").lower()
        self.username = os.getenv("SMTP_USERNAME", "")
        self.password = os.getenv("SMTP_PASSWORD", "")
        self.sender = os.getenv("SMTP_FROM", "")
        if self.security not in {"starttls", "ssl", "none"}: raise RuntimeError("SMTP_SECURITY must be starttls, ssl, or none.")
        if os.getenv("NODE_ENV") == "production" and not all((self.host, self.sender)):
            raise RuntimeError("SMTP_HOST and SMTP_FROM are required in production.")

    async def send_credentials(self, recipient: str, academy: str, username: str, password: str) -> None:
        if not self.host or not self.sender: raise RuntimeError("SMTP is not configured.")
        message = EmailMessage()
        message["Subject"] = f"Your {academy} administrator account"
        message["From"] = self.sender
        message["To"] = recipient
        origin = os.getenv("USER_APP_ORIGIN", "http://localhost:5173")
        message.set_content(f"Your AMS academy administrator account is ready.\n\nAcademy: {academy}\nUsername: {username}\nTemporary password: {password}\nSign in: {origin}\n\nYou must change this password after signing in.")
        await asyncio.to_thread(self._send, message)

    def _send(self, message: EmailMessage) -> None:
        client_type = smtplib.SMTP_SSL if self.security == "ssl" else smtplib.SMTP
        with client_type(self.host, self.port, timeout=15) as client:
            if self.security == "starttls": client.starttls()
            if self.username: client.login(self.username, self.password)
            client.send_message(message)
