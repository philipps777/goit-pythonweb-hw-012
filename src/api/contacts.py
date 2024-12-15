from typing import List, Optional

from fastapi import APIRouter, HTTPException, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.database.models import User
from src.schemas.contact import ContactCreate, ContactUpdate, ContactResponse
from src.services.contacts import ContactService
from src.api.auth import get_current_user

router = APIRouter(prefix="/contacts", tags=["contacts"])

@router.get("/", response_model=List[ContactResponse])
async def read_contacts(
    skip: int = 0,
    limit: int = 100,
    search: Optional[str] = Query(None, description="Search by name, last name or email"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
        Get a list of contacts.

        Args:
            skip (int): The number of contacts to skip.
            limit (int): The maximum number of contacts to return.
            search (Optional[str]): The search query.
            db (AsyncSession): The database session.
            current_user (User): The current user.

        Returns:
            List[ContactResponse]: The list of contacts.
        """
    contact_service = ContactService(db)
    if search:
        contacts = await contact_service.search_contacts(search, skip, limit, current_user.id)
    else:
        contacts = await contact_service.get_contacts(skip, limit, current_user.id)
    return contacts

@router.get("/birthdays/", response_model=List[ContactResponse])
async def upcoming_birthdays(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
       Get a list of upcoming birthdays.

       Args:
           db (AsyncSession): The database session.
           current_user (User): The current user.

       Returns:
           List[ContactResponse]: The list of contacts with upcoming birthdays.
       """
    contact_service = ContactService(db)
    contacts = await contact_service.get_upcoming_birthdays(current_user.id)
    return contacts

@router.get("/{contact_id}", response_model=ContactResponse)
async def read_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
        Get a contact by ID.

        Args:
            contact_id (int): The ID of the contact.
            db (AsyncSession): The database session.
            current_user (User): The current user.

        Returns:
            ContactResponse: The contact.

        Raises:
            HTTPException: If the contact is not found.
        """
    contact_service = ContactService(db)
    contact = await contact_service.get_contact(contact_id, current_user.id)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.post("/", response_model=ContactResponse, status_code=status.HTTP_201_CREATED)
async def create_contact(
    body: ContactCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
        Create a new contact.

        Args:
            body (ContactCreate): The contact data.
            db (AsyncSession): The database session.
            current_user (User): The current user.

        Returns:
            ContactResponse: The created contact.
        """
    contact_service = ContactService(db)
    return await contact_service.create_contact(body, current_user.id)

@router.put("/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: int,
    body: ContactUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
        Update a contact.

        Args:
            contact_id (int): The ID of the contact.
            body (ContactUpdate): The updated contact data.
            db (AsyncSession): The database session.
            current_user (User): The current user.

        Returns:
            ContactResponse: The updated contact.

        Raises:
            HTTPException: If the contact is not found.
        """
    contact_service = ContactService(db)
    contact = await contact_service.update_contact(contact_id, body, current_user.id)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact

@router.delete("/{contact_id}", response_model=ContactResponse)
async def delete_contact(
    contact_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
       Delete a contact.

       Args:
           contact_id (int): The ID of the contact.
           db (AsyncSession): The database session.
           current_user (User): The current user.

       Returns:
           ContactResponse: The deleted contact.

       Raises:
           HTTPException: If the contact is not found.
       """
    contact_service = ContactService(db)
    contact = await contact_service.delete_contact(contact_id, current_user.id)
    if contact is None:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact