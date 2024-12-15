import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.repository.contacts import ContactRepository
from src.schemas.contact import ContactCreate, ContactUpdate
from src.database.models import Contact
from datetime import date


@pytest.mark.asyncio
async def test_create_contact(async_session: AsyncSession):
    repo = ContactRepository(async_session)
    user_id = 1
    contact_data = ContactCreate(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="123-456-7890",
        birth_date=date(1990, 1, 1),
    )

    contact = await repo.create(contact_data, user_id)

    assert contact.id is not None
    assert contact.first_name == "John"
    assert contact.last_name == "Doe"
    assert contact.email == "john@example.com"
    assert contact.phone == "123-456-7890"
    assert contact.birth_date == date(1990, 1, 1)
    assert contact.user_id == user_id

    db_contact = await async_session.get(Contact, contact.id)
    assert db_contact is not None
    assert db_contact.email == "john@example.com"


@pytest.mark.asyncio
async def test_get_contact_by_id(async_session: AsyncSession):
    repo = ContactRepository(async_session)
    user_id = 1
    contact_data = ContactCreate(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="123-456-7890",
        birth_date=date(1990, 1, 1),
    )
    contact = await repo.create(contact_data, user_id)

    fetched_contact = await repo.get_by_id(contact.id, user_id)

    assert fetched_contact is not None
    assert fetched_contact.id == contact.id
    assert fetched_contact.first_name == "John"
    assert fetched_contact.phone == "123-456-7890"


@pytest.mark.asyncio
async def test_update_contact(async_session: AsyncSession):
    repo = ContactRepository(async_session)
    user_id = 1
    contact_data = ContactCreate(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="123-456-7890",
        birth_date=date(1990, 1, 1),
    )
    contact = await repo.create(contact_data, user_id)

    updated_data = ContactUpdate(email="new_email@example.com")

    updated_contact = await repo.update(contact.id, updated_data, user_id)

    assert updated_contact is not None
    assert updated_contact.email == "new_email@example.com"


@pytest.mark.asyncio
async def test_delete_contact(async_session: AsyncSession):
    repo = ContactRepository(async_session)
    user_id = 1
    contact_data = ContactCreate(
        first_name="John",
        last_name="Doe",
        email="john@example.com",
        phone="123-456-7890",
        birth_date=date(1990, 1, 1),
    )
    contact = await repo.create(contact_data, user_id)

    deleted_contact = await repo.delete(contact.id, user_id)

    assert deleted_contact is not None
    assert deleted_contact.id == contact.id

    db_contact = await async_session.get(Contact, contact.id)
    assert db_contact is None
