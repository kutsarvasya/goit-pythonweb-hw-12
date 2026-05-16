from datetime import date, timedelta

import pytest


def contact_payload(
    first_name: str = "John",
    last_name: str = "Doe",
    email: str = "john@example.com",
    birthday: str = "1995-05-10",
):
    return {
        "first_name": first_name,
        "last_name": last_name,
        "email": email,
        "phone": "+31612345678",
        "birthday": birthday,
        "additional_data": "Friend",
    }


@pytest.mark.asyncio
async def test_create_contact_route(client, token):
    response = await client.post(
        "/api/contacts/",
        json=contact_payload(),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 201

    data = response.json()

    assert data["first_name"] == "John"
    assert data["email"] == "john@example.com"


@pytest.mark.asyncio
async def test_get_contacts_route(client, token):
    await client.post(
        "/api/contacts/",
        json=contact_payload(),
        headers={"Authorization": f"Bearer {token}"},
    )

    response = await client.get(
        "/api/contacts/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1


@pytest.mark.asyncio
async def test_get_contact_by_id_route(client, token):
    create_response = await client.post(
        "/api/contacts/",
        json=contact_payload(),
        headers={"Authorization": f"Bearer {token}"},
    )

    contact_id = create_response.json()["id"]

    response = await client.get(
        f"/api/contacts/{contact_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["id"] == contact_id


@pytest.mark.asyncio
async def test_get_contact_by_id_not_found_route(client, token):
    response = await client.get(
        "/api/contacts/999",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_update_contact_route(client, token):
    create_response = await client.post(
        "/api/contacts/",
        json=contact_payload(),
        headers={"Authorization": f"Bearer {token}"},
    )

    contact_id = create_response.json()["id"]

    response = await client.put(
        f"/api/contacts/{contact_id}",
        json=contact_payload(
            first_name="Updated",
            email="updated@example.com",
        ),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.json()["first_name"] == "Updated"
    assert response.json()["email"] == "updated@example.com"


@pytest.mark.asyncio
async def test_update_contact_not_found_route(client, token):
    response = await client.put(
        "/api/contacts/999",
        json=contact_payload(first_name="Updated"),
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_contact_route(client, token):
    create_response = await client.post(
        "/api/contacts/",
        json=contact_payload(),
        headers={"Authorization": f"Bearer {token}"},
    )

    contact_id = create_response.json()["id"]

    response = await client.delete(
        f"/api/contacts/{contact_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200

    get_response = await client.get(
        f"/api/contacts/{contact_id}",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert get_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_contact_not_found_route(client, token):
    response = await client.delete(
        "/api/contacts/999",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 404


@pytest.mark.asyncio
async def test_search_contacts_route(client, token):
    await client.post(
        "/api/contacts/",
        json=contact_payload(
            first_name="Alice",
            email="alice@example.com",
        ),
        headers={"Authorization": f"Bearer {token}"},
    )

    response = await client.get(
        "/api/contacts/search/?query=Alice",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["first_name"] == "Alice"


@pytest.mark.asyncio
async def test_get_upcoming_birthdays_route(client, token):
    birthday = date.today() + timedelta(days=3)

    await client.post(
        "/api/contacts/",
        json=contact_payload(
            first_name="Birthday",
            email="birthday@example.com",
            birthday=str(birthday),
        ),
        headers={"Authorization": f"Bearer {token}"},
    )

    response = await client.get(
        "/api/contacts/birthdays/",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert len(response.json()) == 1
    assert response.json()[0]["first_name"] == "Birthday"


@pytest.mark.asyncio
async def test_get_contacts_unauthorized(client):
    response = await client.get("/api/contacts/")

    assert response.status_code == 401
