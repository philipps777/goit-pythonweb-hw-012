import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from src.database.models import User
from src.repository.users import UserRepository
from src.schemas.user import UserCreate
from src.database.models import Role


@pytest.mark.asyncio
async def test_create_user(async_session: AsyncSession):
    assert isinstance(async_session, AsyncSession)

    repo = UserRepository(async_session)
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        role=Role.USER,
        password="secure_password",
    )

    user = await repo.create_user(user_data, hashed_password="hashed_password")

    assert user.id is not None
    assert user.username == "testuser"
    assert user.email == "test@example.com"
    assert user.password == "hashed_password"
    assert user.role == Role.USER

    db_user = await async_session.get(User, user.id)
    assert db_user is not None
    assert db_user.email == "test@example.com"


@pytest.mark.asyncio
async def test_get_user_by_email(async_session: AsyncSession):
    repo = UserRepository(async_session)
    user_data = UserCreate(
        username="testuser",
        email="test@example.com",
        role=Role.USER,
        password="secure_password",
    )
    await repo.create_user(user_data, hashed_password="hashed_password")

    user = await repo.get_user_by_email("test@example.com")

    assert user is not None
    assert user.email == "test@example.com"
    assert user.username == "testuser"
