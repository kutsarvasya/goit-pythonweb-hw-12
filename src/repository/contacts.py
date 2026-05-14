from datetime import date, timedelta
from typing import List

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import Contact, User
from src.schemas import ContactModel, ContactUpdate


class ContactRepository:
    """
    Repository for contact database operations.

    Provides methods for creating, reading, updating,
    deleting, searching contacts, and retrieving upcoming birthdays.
    All operations are limited to the current authenticated user.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize contact repository.

        Args:
            session: Async database session.
        """

        self.db = session

    async def get_contacts(self, skip: int, limit: int, user: User) -> List[Contact]:
        """
        Retrieve contacts for a specific user.

        Args:
            skip: Number of records to skip.
            limit: Maximum number of records to return.
            user: Current authenticated user.

        Returns:
            List of user contacts.
        """

        stmt = (
            select(Contact).where(Contact.user_id == user.id).offset(skip).limit(limit)
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_contact_by_id(self, contact_id: int, user: User) -> Contact | None:
        """
        Retrieve a contact by ID for a specific user.

        Args:
            contact_id: Contact identifier.
            user: Current authenticated user.

        Returns:
            Contact object if found, otherwise None.
        """

        stmt = select(Contact).where(
            Contact.id == contact_id,
            Contact.user_id == user.id,
        )
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_contact(self, body: ContactModel, user: User) -> Contact:
        """
        Create a new contact for a specific user.

        Args:
            body: Contact creation data.
            user: Current authenticated user.

        Returns:
            Created contact object.
        """

        contact = Contact(
            **body.model_dump(),
            user_id=user.id,
        )
        self.db.add(contact)
        await self.db.commit()
        await self.db.refresh(contact)
        return contact

    async def update_contact(
        self,
        contact_id: int,
        body: ContactUpdate,
        user: User,
    ) -> Contact | None:
        """
        Update an existing contact.

        Args:
            contact_id: Contact identifier.
            body: Contact update data.
            user: Current authenticated user.

        Returns:
            Updated contact object if found, otherwise None.
        """

        contact = await self.get_contact_by_id(contact_id, user)

        if contact:
            for key, value in body.model_dump().items():
                setattr(contact, key, value)

            await self.db.commit()
            await self.db.refresh(contact)

        return contact

    async def remove_contact(self, contact_id: int, user: User) -> Contact | None:
        """
        Delete a contact by ID.

        Args:
            contact_id: Contact identifier.
            user: Current authenticated user.

        Returns:
            Deleted contact object if found, otherwise None.
        """

        contact = await self.get_contact_by_id(contact_id, user)

        if contact:
            await self.db.delete(contact)
            await self.db.commit()

        return contact

    async def search_contacts(self, query: str, user: User) -> List[Contact]:
        """
        Search user contacts by first name, last name, or email.

        Args:
            query: Search query string.
            user: Current authenticated user.

        Returns:
            List of matching contacts.
        """

        stmt = select(Contact).where(
            Contact.user_id == user.id,
            or_(
                Contact.first_name.ilike(f"%{query}%"),
                Contact.last_name.ilike(f"%{query}%"),
                Contact.email.ilike(f"%{query}%"),
            ),
        )
        result = await self.db.execute(stmt)
        return list(result.scalars().all())

    async def get_upcoming_birthdays(self, user: User) -> List[Contact]:
        """
        Retrieve contacts with birthdays in the next seven days.

        Args:
            user: Current authenticated user.

        Returns:
            List of contacts with upcoming birthdays.
        """

        today = date.today()
        end_date = today + timedelta(days=7)

        stmt = select(Contact).where(Contact.user_id == user.id)
        result = await self.db.execute(stmt)
        contacts = result.scalars().all()

        upcoming = []
        for contact in contacts:
            birthday_this_year = contact.birthday.replace(year=today.year)

            if birthday_this_year < today:
                birthday_this_year = birthday_this_year.replace(year=today.year + 1)

            if today <= birthday_this_year <= end_date:
                upcoming.append(contact)

        return upcoming
