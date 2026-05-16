import httpx
from pydantic import EmailStr

from src.conf.config import config
from src.services.auth import create_email_token

BREVO_API_URL = "https://api.brevo.com/v3/smtp/email"


async def send_brevo_email(
    email: EmailStr,
    subject: str,
    html_content: str,
):
    headers = {
        "accept": "application/json",
        "api-key": config.BREVO_API_KEY,
        "content-type": "application/json",
    }

    payload = {
        "sender": {
            "name": config.MAIL_FROM_NAME,
            "email": str(config.MAIL_FROM),
        },
        "to": [
            {
                "email": str(email),
            }
        ],
        "subject": subject,
        "htmlContent": html_content,
    }

    async with httpx.AsyncClient(timeout=15) as client:
        response = await client.post(
            BREVO_API_URL,
            headers=headers,
            json=payload,
        )

    response.raise_for_status()


async def send_email(email: EmailStr, username: str, host: str):
    """
    Send email verification message using Brevo API.
    """

    token_verification = await create_email_token({"sub": email})

    confirm_url = f"{host}api/auth/confirmed_email/{token_verification}"

    html_content = f"""
    <h2>Hello, {username}!</h2>
    <p>Please confirm your email address.</p>
    <p>
        <a href="{confirm_url}">Confirm email</a>
    </p>
    """

    await send_brevo_email(
        email=email,
        subject="Confirm your email",
        html_content=html_content,
    )


async def send_reset_password_email(
    email: EmailStr,
    username: str,
    host: str,
):
    """
    Send password reset message using Brevo API.
    """

    token_reset = await create_email_token({"sub": email})

    reset_url = f"{host}api/auth/reset_password/{token_reset}"

    html_content = f"""
    <h2>Hello, {username}!</h2>
    <p>You requested a password update.</p>
    <p>
        <a href="{reset_url}">Update password</a>
    </p>
    <p>If you did not request this, you can ignore this email.</p>
    """

    await send_brevo_email(
        email=email,
        subject="Account access request",
        html_content=html_content,
    )
