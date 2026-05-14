from typing import List

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.database.models import User
from src.repository.contacts import ContactRepository
from src.schemas import ContactModel, ContactResponse, ContactUpdate
from src.services.auth import get_current_user

router = APIRouter(prefix="/contacts", tags=["contacts"])


@router.get("/", response_model=List[ContactResponse])
async def get_contacts(
    skip: int = 0,
    limit: int = 10,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieve a list of user contacts.

    Args:
        skip: Number of records to skip.
        limit: Maximum number of records to return.
        db: Database session.
        user: Current authenticated user.

    Returns:
        List of contacts.
    """

    repo = ContactRepository(db)
    return await repo.get_contacts(skip, limit, user)


@router.get("/search/", response_model=List[ContactResponse])
async def search_contacts(
    query: str = Query(..., min_length=1),
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Search contacts by first name, last name, or email.

    Args:
        query: Search query string.
        db: Database session.
        user: Current authenticated user.

    Returns:
        List of matching contacts.
    """

    repo = ContactRepository(db)
    return await repo.search_contacts(query, user)


@router.get("/birthdays/", response_model=List[ContactResponse])
async def get_upcoming_birthdays(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieve contacts with upcoming birthdays.

    Returns contacts whose birthdays occur
    within the next seven days.

    Args:
        db: Database session.
        user: Current authenticated user.

    Returns:
        List of contacts with upcoming birthdays.
    """

    repo = ContactRepository(db)
    return await repo.get_upcoming_birthdays(user)


@router.get("/{contact_id}", response_model=ContactResponse)
async def get_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Retrieve contact by ID.

    Args:
        contact_id: Contact identifier.
        db: Database session.
        user: Current authenticated user.

    Returns:
        Contact object.

    Raises:
        HTTPException: If contact is not found.
    """

    repo = ContactRepository(db)
    contact = await repo.get_contact_by_id(contact_id, user)

    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )

    return contact


@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactModel,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Create a new contact.

    Args:
        body: Contact data.
        db: Database session.
        user: Current authenticated user.

    Returns:
        Created contact object.
    """

    repo = ContactRepository(db)
    return await repo.create_contact(body, user)


@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    body: ContactUpdate,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Update existing contact.

    Args:
        contact_id: Contact identifier.
        body: Updated contact data.
        db: Database session.
        user: Current authenticated user.

    Returns:
        Updated contact object.

    Raises:
        HTTPException: If contact is not found.
    """

    repo = ContactRepository(db)
    contact = await repo.update_contact(contact_id, body, user)

    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )

    return contact


@router.delete("/{contact_id}", response_model=ContactResponse)
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    """
    Delete contact by ID.

    Args:
        contact_id: Contact identifier.
        db: Database session.
        user: Current authenticated user.

    Returns:
        Deleted contact object.

    Raises:
        HTTPException: If contact is not found.
    """

    repo = ContactRepository(db)
    contact = await repo.remove_contact(contact_id, user)

    if contact is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Contact not found",
        )

    return contact
