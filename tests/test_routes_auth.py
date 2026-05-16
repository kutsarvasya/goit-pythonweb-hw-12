from unittest.mock import AsyncMock, patch

import pytest

from src.repository.users import UserRepository
from src.services.auth import create_email_token, Hash


@pytest.mark.asyncio
async def test_register_user(client):
    with patch("src.api.auth.send_email", new_callable=AsyncMock):
        response = await client.post(
            "/api/auth/register",
            json={
                "username": "routeuser",
                "email": "routeuser@example.com",
                "password": "12345678",
            },
        )

    assert response.status_code == 201

    data = response.json()

    assert data["username"] == "routeuser"
    assert data["email"] == "routeuser@example.com"
    assert "hashed_password" not in data


@pytest.mark.asyncio
async def test_register_existing_email(client, test_user):
    response = await client.post(
        "/api/auth/register",
        json={
            "username": "anotheruser",
            "email": test_user.email,
            "password": "12345678",
        },
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_register_existing_username(client, test_user):
    response = await client.post(
        "/api/auth/register",
        json={
            "username": test_user.username,
            "email": "another@example.com",
            "password": "12345678",
        },
    )

    assert response.status_code == 409


@pytest.mark.asyncio
async def test_login_user(client, test_user):
    response = await client.post(
        "/api/auth/login",
        data={
            "username": "testuser",
            "password": "12345678",
        },
    )

    assert response.status_code == 200

    data = response.json()

    assert "access_token" in data
    assert data["token_type"] == "bearer"


@pytest.mark.asyncio
async def test_login_wrong_password(client, test_user):
    response = await client.post(
        "/api/auth/login",
        data={
            "username": "testuser",
            "password": "wrongpassword",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_login_user_not_found(client):
    response = await client.post(
        "/api/auth/login",
        data={
            "username": "unknown",
            "password": "12345678",
        },
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_confirmed_email(client, db_session):
    repo = UserRepository(db_session)

    user_data = {
        "username": "confirmuser",
        "email": "confirm@example.com",
        "password": "12345678",
    }

    with patch("src.api.auth.send_email", new_callable=AsyncMock):
        response = await client.post("/api/auth/register", json=user_data)

    assert response.status_code == 201

    token = await create_email_token({"sub": user_data["email"]})

    response = await client.get(f"/api/auth/confirmed_email/{token}")

    assert response.status_code == 200
    assert response.json()["message"] == "Email confirmed successfully"

    user = await repo.get_user_by_email(user_data["email"])
    assert user.confirmed is True


@pytest.mark.asyncio
async def test_confirmed_email_already_confirmed(client, test_user):
    token = await create_email_token({"sub": test_user.email})

    response = await client.get(f"/api/auth/confirmed_email/{token}")

    assert response.status_code == 200
    assert response.json()["message"] == "Your email is already confirmed"


@pytest.mark.asyncio
async def test_request_email_user_not_found(client):
    response = await client.post(
        "/api/auth/request_email",
        json={"email": "missing@example.com"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Check your email for confirmation"


@pytest.mark.asyncio
async def test_request_email_already_confirmed(client, test_user):
    response = await client.post(
        "/api/auth/request_email",
        json={"email": test_user.email},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Your email is already confirmed"


@pytest.mark.asyncio
async def test_request_password_reset(client, test_user):
    with patch("src.api.auth.send_reset_password_email", new_callable=AsyncMock):
        response = await client.post(
            "/api/auth/request_password_reset",
            json={"email": test_user.email},
        )

    assert response.status_code == 200
    assert response.json()["message"] == "Check your email for password reset"


@pytest.mark.asyncio
async def test_request_password_reset_user_not_found(client):
    response = await client.post(
        "/api/auth/request_password_reset",
        json={"email": "missing@example.com"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Check your email for password reset"


@pytest.mark.asyncio
async def test_reset_password(client, db_session, test_user):
    token = await create_email_token({"sub": test_user.email})

    response = await client.post(
        f"/api/auth/reset_password/{token}",
        json={"password": "newpassword123"},
    )

    assert response.status_code == 200
    assert response.json()["message"] == "Password updated successfully"

    repo = UserRepository(db_session)
    user = await repo.get_user_by_email(test_user.email)

    assert Hash.verify_password("newpassword123", user.hashed_password)
