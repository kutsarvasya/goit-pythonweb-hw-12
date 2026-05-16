from datetime import date, timedelta

import pytest

from src.repository.contacts import ContactRepository
from src.schemas import ContactModel, ContactUpdate


def contact_data(
    first_name: str = "John",
    last_name: str = "Doe",
    email: str = "john@example.com",
    birthday: date | None = None,
):
    return ContactModel(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone="+31612345678",
        birthday=birthday or date(1995, 5, 10),
        additional_data="Friend",
    )


@pytest.mark.asyncio
async def test_create_contact(db_session, test_user):
    repo = ContactRepository(db_session)

    contact = await repo.create_contact(contact_data(), test_user)

    assert contact.id is not None
    assert contact.first_name == "John"
    assert contact.user_id == test_user.id


@pytest.mark.asyncio
async def test_get_contacts(db_session, test_user):
    repo = ContactRepository(db_session)

    await repo.create_contact(contact_data(), test_user)

    contacts = await repo.get_contacts(0, 10, test_user)

    assert len(contacts) == 1
    assert contacts[0].email == "john@example.com"


@pytest.mark.asyncio
async def test_get_contact_by_id(db_session, test_user):
    repo = ContactRepository(db_session)

    created_contact = await repo.create_contact(contact_data(), test_user)

    contact = await repo.get_contact_by_id(created_contact.id, test_user)

    assert contact is not None
    assert contact.id == created_contact.id


@pytest.mark.asyncio
async def test_get_contact_by_id_not_found(db_session, test_user):
    repo = ContactRepository(db_session)

    contact = await repo.get_contact_by_id(999, test_user)

    assert contact is None


@pytest.mark.asyncio
async def test_update_contact(db_session, test_user):
    repo = ContactRepository(db_session)

    created_contact = await repo.create_contact(contact_data(), test_user)

    update_data = ContactUpdate(
        first_name="Updated",
        last_name="Doe",
        email="updated@example.com",
        phone="+31687654321",
        birthday=date(1996, 6, 15),
        additional_data="Updated data",
    )

    updated_contact = await repo.update_contact(
        created_contact.id,
        update_data,
        test_user,
    )

    assert updated_contact is not None
    assert updated_contact.first_name == "Updated"
    assert updated_contact.email == "updated@example.com"


@pytest.mark.asyncio
async def test_update_contact_not_found(db_session, test_user):
    repo = ContactRepository(db_session)

    update_data = ContactUpdate(
        first_name="Updated",
        last_name="Doe",
        email="updated@example.com",
        phone="+31687654321",
        birthday=date(1996, 6, 15),
        additional_data="Updated data",
    )

    updated_contact = await repo.update_contact(
        999,
        update_data,
        test_user,
    )

    assert updated_contact is None


@pytest.mark.asyncio
async def test_remove_contact(db_session, test_user):
    repo = ContactRepository(db_session)

    created_contact = await repo.create_contact(contact_data(), test_user)

    removed_contact = await repo.remove_contact(created_contact.id, test_user)

    assert removed_contact is not None
    assert removed_contact.id == created_contact.id

    contact = await repo.get_contact_by_id(created_contact.id, test_user)

    assert contact is None


@pytest.mark.asyncio
async def test_remove_contact_not_found(db_session, test_user):
    repo = ContactRepository(db_session)

    removed_contact = await repo.remove_contact(999, test_user)

    assert removed_contact is None


@pytest.mark.asyncio
async def test_search_contacts(db_session, test_user):
    repo = ContactRepository(db_session)

    await repo.create_contact(
        contact_data(
            first_name="Alice",
            last_name="Smith",
            email="alice@example.com",
        ),
        test_user,
    )

    contacts = await repo.search_contacts("Alice", test_user)

    assert len(contacts) == 1
    assert contacts[0].first_name == "Alice"


@pytest.mark.asyncio
async def test_get_upcoming_birthdays(db_session, test_user):
    repo = ContactRepository(db_session)

    today = date.today()
    birthday = today + timedelta(days=3)

    await repo.create_contact(
        contact_data(
            first_name="Birthday",
            last_name="User",
            email="birthday@example.com",
            birthday=birthday,
        ),
        test_user,
    )

    contacts = await repo.get_upcoming_birthdays(test_user)

    assert len(contacts) == 1
    assert contacts[0].first_name == "Birthday"
