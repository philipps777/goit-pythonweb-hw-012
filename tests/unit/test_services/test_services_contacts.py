import pytest
from datetime import date, timedelta
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result

from src.services.contacts import ContactRepository
from src.database.models import Contact
from src.schemas.contact import ContactCreate, ContactUpdate


@pytest.mark.asyncio
async def test_get_all_contacts():
    mock_session = AsyncMock(spec=AsyncSession)
    mock_result = AsyncMock(spec=Result)
    mock_result.scalars().all.return_value = [
        Contact(id=1, first_name="John", last_name="Doe", email="john.doe@example.com"),
        Contact(id=2, first_name="Jane", last_name="Smith", email="jane.smith@example.com"),
    ]
    mock_session.execute.return_value = mock_result

    repo = ContactRepository(mock_session)
    contacts = await repo.get_all(user_id=1)

    assert len(contacts) == 2
    assert contacts[0].first_name == "John"
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_contact_by_id():
    mock_session = AsyncMock(spec=AsyncSession)
    mock_result = AsyncMock(spec=Result)
    mock_result.scalar_one_or_none.return_value = Contact(
        id=1, first_name="John", last_name="Doe", email="john.doe@example.com"
    )
    mock_session.execute.return_value = mock_result

    repo = ContactRepository(mock_session)
    contact = await repo.get_by_id(contact_id=1, user_id=1)

    assert contact is not None
    assert contact.first_name == "John"
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_create_contact():
    mock_session = AsyncMock(spec=AsyncSession)
    body = ContactCreate(
        first_name="John",
        last_name="Doe",
        email="john.doe@example.com",
        phone="123456789",
        birth_date=date(1990, 1, 1),
    )

    repo = ContactRepository(mock_session)
    created_contact = await repo.create(body, user_id=1)

    assert created_contact is not None
    assert created_contact.first_name == "John"
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_update_contact():
    mock_session = AsyncMock(spec=AsyncSession)
    mock_result = AsyncMock(spec=Result)
    mock_result.scalar_one_or_none.return_value = Contact(
        id=1, first_name="John", last_name="Doe", email="john.doe@example.com"
    )
    mock_session.execute.return_value = mock_result
    body = ContactUpdate(email="new.email@example.com")

    repo = ContactRepository(mock_session)
    updated_contact = await repo.update(contact_id=1, body=body, user_id=1)

    assert updated_contact is not None
    assert updated_contact.email == "new.email@example.com"
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_delete_contact():
    mock_session = AsyncMock(spec=AsyncSession)
    mock_result = AsyncMock(spec=Result)
    mock_result.scalar_one_or_none.return_value = Contact(
        id=1, first_name="John", last_name="Doe", email="john.doe@example.com"
    )
    mock_session.execute.return_value = mock_result

    repo = ContactRepository(mock_session)
    deleted_contact = await repo.delete(contact_id=1, user_id=1)

    assert deleted_contact is not None
    assert deleted_contact.first_name == "John"
    mock_session.delete.assert_called_once()
    mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_search_contacts():
    mock_session = AsyncMock(spec=AsyncSession)
    mock_result = AsyncMock(spec=Result)
    mock_result.scalars().all.return_value = [
        Contact(id=1, first_name="John", last_name="Doe", email="john.doe@example.com")
    ]
    mock_session.execute.return_value = mock_result

    repo = ContactRepository(mock_session)
    contacts = await repo.search_contacts("John", user_id=1)

    assert len(contacts) == 1
    assert contacts[0].first_name == "John"
    mock_session.execute.assert_called_once()


@pytest.mark.asyncio
async def test_get_upcoming_birthdays():
    mock_session = AsyncMock(spec=AsyncSession)
    mock_result = AsyncMock(spec=Result)
    mock_result.scalars().all.return_value = [
        Contact(
            id=1,
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            birth_date=date.today() + timedelta(days=3),
        )
    ]
    mock_session.execute.return_value = mock_result

    repo = ContactRepository(mock_session)
    birthdays = await repo.get_upcoming_birthdays(user_id=1)

    assert len(birthdays) == 1
    assert birthdays[0].first_name == "John"
    mock_session.execute.assert_called_once()
