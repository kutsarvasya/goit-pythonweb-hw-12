from pathlib import Path

from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType
from fastapi_mail.errors import ConnectionErrors
from pydantic import EmailStr

from src.conf.config import config
from src.services.auth import create_email_token

conf = ConnectionConfig(
    MAIL_USERNAME=config.MAIL_USERNAME,
    MAIL_PASSWORD=config.MAIL_PASSWORD,
    MAIL_FROM=config.MAIL_FROM,
    MAIL_PORT=config.MAIL_PORT,
    MAIL_SERVER=config.MAIL_SERVER,
    MAIL_FROM_NAME=config.MAIL_FROM_NAME,
    MAIL_STARTTLS=config.MAIL_STARTTLS,
    MAIL_SSL_TLS=config.MAIL_SSL_TLS,
    USE_CREDENTIALS=config.USE_CREDENTIALS,
    VALIDATE_CERTS=config.VALIDATE_CERTS,
    TEMPLATE_FOLDER=Path(__file__).parent / "templates",
)


async def send_email(email: EmailStr, username: str, host: str):
    """
    Send email verification message.

    Generates verification token and sends
    HTML email with confirmation link.

    Args:
        email: Recipient email address.
        username: Username of recipient.
        host: Application base URL.
    """

    try:
        token_verification = await create_email_token({"sub": email})

        message = MessageSchema(
            subject="Confirm your email",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_verification,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)

        await fm.send_message(
            message,
            template_name="verify_email.html",
        )

    except ConnectionErrors as err:
        print(err)


async def send_reset_password_email(
    email: EmailStr,
    username: str,
    host: str,
):
    """
    Send password reset email.

    Generates password reset token
    and sends email with reset link.

    Args:
        email: Recipient email address.
        username: Username of recipient.
        host: Application base URL.
    """

    try:
        token_reset = await create_email_token({"sub": email})

        message = MessageSchema(
            subject="Account access request",
            recipients=[email],
            template_body={
                "host": host,
                "username": username,
                "token": token_reset,
            },
            subtype=MessageType.html,
        )

        fm = FastMail(conf)

        await fm.send_message(
            message,
            template_name="reset_password.html",
        )

    except ConnectionErrors as err:
        print(err)
