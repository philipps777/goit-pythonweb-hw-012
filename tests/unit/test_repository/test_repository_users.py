# import asyncio
#
# import pytest
# from unittest.mock import AsyncMock
# from sqlalchemy.ext.asyncio import AsyncSession
# from src.repository.users import UserRepository
# from src.database.models import User, Role
# from src.schemas.user import UserCreate
#
# @pytest.mark.asyncio
# async def test_create_user():
#     mock_session = AsyncMock(spec=AsyncSession)
#     body = UserCreate(username="alice", email="alice@example.com", role="user", password="secure_password")
#     hashed_password = "hashed_password"
#
#     repo = UserRepository(mock_session)
#     created_user = await repo.create_user(body=body, hashed_password=hashed_password)
#
#     assert created_user.username == "alice"
#     assert created_user.email == "alice@example.com"
#     assert created_user.password == hashed_password
#     assert created_user.role == Role.USER
#     mock_session.add.assert_called_once()
#     mock_session.commit.assert_called_once()
#     mock_session.refresh.assert_called_once()
#
# @pytest.mark.asyncio
# async def test_get_user_by_email_found(mocker):
#     mock_session = mocker.AsyncMock(spec=AsyncSession)
#     mock_result = mocker.AsyncMock()
#     mock_user = User(username="alice", email="alice@example.com", password="hashed_password", role=Role.USER)
#     mock_result.scalar_one_or_none.return_value = mock_user
#     mock_session.execute.return_value = mock_result
#
#     repo = UserRepository(mock_session)
#     user = await repo.get_user_by_email(email="alice@example.com")
#
#     assert user is not None
#     assert user.email == "alice@example.com"
#     mock_session.execute.assert_called_once()
#
# @pytest.mark.asyncio
# async def test_get_user_by_email_not_found(mocker):
#     mock_session = mocker.AsyncMock(spec=AsyncSession)
#     mock_result = mocker.AsyncMock()
#     mock_result.scalar_one_or_none.return_value = None
#     mock_session.execute.return_value = mock_result
#
#     repo = UserRepository(mock_session)
#     user = await repo.get_user_by_email(email="nonexistent@example.com")
#
#     assert user is None
#     mock_session.execute.assert_called_once()


import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.engine import Result

from src.repository.users import UserRepository
from src.database.models import User, Role
from src.schemas.user import UserCreate


@pytest.mark.asyncio
async def test_create_user():
    mock_session = AsyncMock(spec=AsyncSession)
    body = UserCreate(username="alice", email="alice@example.com", role="user", password="secure_password")
    hashed_password = "hashed_password"

    repo = UserRepository(mock_session)
    created_user = await repo.create_user(body=body, hashed_password=hashed_password)

    assert created_user.username == "alice"
    assert created_user.email == "alice@example.com"
    assert created_user.password == hashed_password
    assert created_user.role == Role.USER
    mock_session.add.assert_called_once()
    mock_session.commit.assert_called_once()
    mock_session.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_get_user_by_email():
    mock_session = AsyncMock(spec=AsyncSession)
    mock_result = AsyncMock(spec=Result)
    mock_result.scalar_one_or_none.return_value = User(
        id=1,
        username="testuser",
        email="testuser@example.com",
        password="hashedpassword123",
        role=Role.USER,
    )
    mock_session.execute.return_value = mock_result
    repo = UserRepository(mock_session)
    user = await repo.get_user_by_email(email="testuser@example.com")

    assert user is not None
    assert user.username == "testuser"
    assert user.email == "testuser@example.com"
    mock_session.execute.assert_called_once()
