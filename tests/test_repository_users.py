import pytest

from src.repository.users import UserRepository
from src.schemas import UserCreate
from src.services.auth import Hash


@pytest.mark.asyncio
async def test_create_user(db_session):
    repo = UserRepository(db_session)

    user_data = UserCreate(
        username="newuser",
        email="newuser@example.com",
        password="12345678",
    )

    hashed_password = Hash.get_password_hash(user_data.password)

    user = await repo.create_user(user_data, hashed_password)

    assert user.id is not None
    assert user.username == user_data.username
    assert user.email == user_data.email
    assert user.hashed_password != user_data.password


@pytest.mark.asyncio
async def test_get_user_by_email(db_session, test_user):
    repo = UserRepository(db_session)

    user = await repo.get_user_by_email(test_user.email)

    assert user is not None
    assert user.email == test_user.email


@pytest.mark.asyncio
async def test_get_user_by_username(db_session, test_user):
    repo = UserRepository(db_session)

    user = await repo.get_user_by_username(test_user.username)

    assert user is not None
    assert user.username == test_user.username


@pytest.mark.asyncio
async def test_confirmed_email(db_session, test_user):
    repo = UserRepository(db_session)

    test_user.confirmed = False
    await db_session.commit()

    await repo.confirmed_email(test_user.email)

    user = await repo.get_user_by_email(test_user.email)

    assert user.confirmed is True


@pytest.mark.asyncio
async def test_update_avatar_url(db_session, test_user):
    repo = UserRepository(db_session)

    avatar_url = "https://example.com/avatar.jpg"

    user = await repo.update_avatar_url(test_user.email, avatar_url)

    assert user is not None
    assert user.avatar == avatar_url


@pytest.mark.asyncio
async def test_update_password(db_session, test_user):
    repo = UserRepository(db_session)

    new_hash = Hash.get_password_hash("newpassword123")

    user = await repo.update_password(test_user.email, new_hash)

    assert user is not None
    assert user.hashed_password == new_hash
