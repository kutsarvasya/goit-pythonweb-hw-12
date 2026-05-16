from pydantic import EmailStr
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    Application configuration settings.
    """

    DB_URL: str

    JWT_SECRET: str
    JWT_ALGORITHM: str
    JWT_EXPIRATION_SECONDS: int

    BREVO_API_KEY: str

    MAIL_FROM: EmailStr
    MAIL_FROM_NAME: str

    REDIS_URL: str

    CLD_NAME: str
    CLD_API_KEY: int
    CLD_API_SECRET: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


config = Settings()
