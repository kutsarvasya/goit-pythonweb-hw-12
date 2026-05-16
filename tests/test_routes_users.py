from io import BytesIO
from unittest.mock import patch

import pytest

from src.database.models import UserRole


@pytest.mark.asyncio
async def test_get_me(client, token):
    response = await client.get(
        "/api/users/me",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    data = response.json()

    assert data["username"] == "testuser"
    assert data["email"] == "test@example.com"


@pytest.mark.asyncio
async def test_get_me_unauthorized(client):
    response = await client.get("/api/users/me")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_update_avatar_as_admin(
    client,
    token,
    test_user,
    db_session,
):
    test_user.role = UserRole.ADMIN
    await db_session.commit()

    with patch(
        "src.services.upload_file.UploadFileService.upload_file",
        return_value="https://example.com/avatar.jpg",
    ):
        response = await client.patch(
            "/api/users/avatar",
            headers={"Authorization": f"Bearer {token}"},
            files={
                "file": (
                    "avatar.jpg",
                    BytesIO(b"fake image"),
                    "image/jpeg",
                )
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["avatar"] == "https://example.com/avatar.jpg"


@pytest.mark.asyncio
async def test_update_avatar_as_user(
    client,
    token,
):
    response = await client.patch(
        "/api/users/avatar",
        headers={"Authorization": f"Bearer {token}"},
        files={
            "file": (
                "avatar.jpg",
                BytesIO(b"fake image"),
                "image/jpeg",
            )
        },
    )

    assert response.status_code == 403
