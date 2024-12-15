from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.contact import ContactCreate, ContactUpdate
from src.repository.contacts import ContactRepository

class ContactService:
    def __init__(self, db: AsyncSession):
        self.repository = ContactRepository(db)

    async def get_contacts(self, skip: int, limit: int):
        """
        Get all contacts

        Args:
            skip (int): The number of contacts to skip.
            limit (int): The maximum number of contacts to return.

        Returns:
            List[Contact]: The list of contacts.
        """
        return await self.repository.get_all(skip, limit)

    async def get_contact(self, contact_id: int):
        """
        Get a contact by ID

        Args:
            contact_id (int): The ID of the contact.

        Returns:
            Contact: The contact.
        """
        return await self.repository.get_by_id(contact_id)

    async def create_contact(self, body: ContactCreate):
        """
        Create a new contact.

        Args:
            body (ContactCreate): The contact data.

        Returns:
            Contact: The created contact.
        """
        return await self.repository.create(body)

    async def update_contact(self, contact_id: int, body: ContactUpdate):
        """
        Update a contact

        Args:
            contact_id (int): The ID of the contact.
            body (ContactUpdate): The updated contact data.

        Returns:
            Contact: The updated contact.
        """
        return await self.repository.update(contact_id, body)

    async def delete_contact(self, contact_id: int):
        """
        Delete a contact

        Args:
            contact_id (int): The ID of the contact.

        Returns:
            Contact: The deleted contact.
        """
        return await self.repository.delete(contact_id)

    async def search_contacts(self, query: str, skip: int, limit: int):
        """
        Search for contacts

        Args:
            query (str): The search query.
            skip (int): The number of contacts to skip.
            limit (int): The maximum number of contacts to return.

        Returns:
            List[Contact]: The list of contacts.
        """
        return await self.repository.search_contacts(query, skip, limit)

    async def get_upcoming_birthdays(self):
        """
        Get a list of upcoming birthdays.

        Returns:
            List[Contact]: The list of contacts with upcoming birthdays.
        """
        return await self.repository.get_upcoming_birthdays()