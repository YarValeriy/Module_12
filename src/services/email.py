"""
Module for sending email notifications.

This module defines an `send_email` function for sending email notifications using the FastAPI Mail library.
The function uses a `ConnectionConfig` object to configure the email server settings based on the application settings.
It then attempts to send an email with the provided details including the email address, username, and host.

"""

from pathlib import Path

from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.conf.config import settings
from src.services.auth import auth_service


conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME="Module_13",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TEMPLATE_FOLDER=Path(__file__).parent / 'templates',
)


async def send_email(email: EmailStr, username: str, host: str):
    """
    Send email notification.

    :param email: Email address of the recipient.
    :type email: EmailStr
    :param username: Username of the recipient.
    :type username: str
    :param host: Host URL for email verification link.
    :type host: str

    Raises:
    ConnectionErrors: If there is an error connecting to the email server.

    """
    try:
        # Create email verification token
        token_verification = auth_service.create_email_token({"sub": email})

        # Create message schema
        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            template_body={"host": host, "username": username, "token": token_verification},
            subtype=MessageType.html
        )

        # Initialize FastMail instance
        fm = FastMail(conf)

        # Send email message
        await fm.send_message(message, template_name="email_template.html")
    except ConnectionErrors as err:
        print(err)

