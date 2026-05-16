import os
import sys
from pathlib import Path

from unittest.mock import AsyncMock
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.pool import NullPool

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR))

os.environ.setdefault(
    "DB_URL",
    "postgresql+asyncpg://postgres:567234@localhost:5432/contacts_test",
)
os.environ.setdefault("TEST_DB_URL", os.environ["DB_URL"])
os.environ.setdefault("JWT_SECRET", "test_secret")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("JWT_EXPIRATION_SECONDS", "3600")
os.environ.setdefault("REDIS_URL", "redis://localhost:6379")
os.environ.setdefault("BREVO_API_KEY", "test_brevo_api_key")
os.environ.setdefault("MAIL_USERNAME", "test@example.com")
os.environ.setdefault("MAIL_PASSWORD", "test_password")
os.environ.setdefault("MAIL_FROM", "test@example.com")
os.environ.setdefault("MAIL_PORT", "465")
os.environ.setdefault("MAIL_SERVER", "smtp.example.com")
os.environ.setdefault("MAIL_FROM_NAME", "Contacts API")
os.environ.setdefault("MAIL_STARTTLS", "False")
os.environ.setdefault("MAIL_SSL_TLS", "True")
os.environ.setdefault("USE_CREDENTIALS", "True")
os.environ.setdefault("VALIDATE_CERTS", "False")

os.environ.setdefault("CLD_NAME", "test")
os.environ.setdefault("CLD_API_KEY", "123456")
os.environ.setdefault("CLD_API_SECRET", "test")

from main import app
from src.database.db import get_db
from src.database.models import Base, User
from src.services.auth import Hash

TEST_DB_URL = os.environ["TEST_DB_URL"]

engine = create_async_engine(
    TEST_DB_URL,
    poolclass=NullPool,
)

TestingSessionLocal = async_sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


@pytest_asyncio.fixture(autouse=True)
async def prepare_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def db_session():
    async with TestingSessionLocal() as session:
        yield session


@pytest_asyncio.fixture
async def client(db_session, monkeypatch):
    async def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    monkeypatch.setattr(
        "src.services.auth.get_cache",
        AsyncMock(return_value=None),
    )
    monkeypatch.setattr(
        "src.services.auth.set_cache",
        AsyncMock(return_value=None),
    )

    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        yield ac

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session):
    user = User(
        username="testuser",
        email="test@example.com",
        hashed_password=Hash.get_password_hash("12345678"),
        confirmed=True,
    )

    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)

    return user


@pytest_asyncio.fixture
async def token(client, test_user):
    response = await client.post(
        "/api/auth/login",
        data={
            "username": "testuser",
            "password": "12345678",
        },
    )

    data = response.json()

    return data["access_token"]
