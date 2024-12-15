from email.mime.text import MIMEText

import pytest
from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from unittest.mock import AsyncMock, patch, MagicMock

from src.services.auth import (
    create_access_token,
    verify_password,
    get_password_hash,
    authenticate_user,
    generate_email_verification_token,
    send_reset_password_email,
)
from src.services.auth import send_reset_password_email
from src.conf.config import config


@pytest.mark.asyncio
async def test_create_access_token():
    data = {"sub": "test@example.com"}
    token = create_access_token(data, expires_delta=15)
    decoded_token = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
    assert decoded_token["sub"] == "test@example.com"
    assert "exp" in decoded_token


def test_verify_password():
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    hashed = pwd_context.hash("password123")
    assert verify_password("password123", hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_get_password_hash():
    hash1 = get_password_hash("password123")
    hash2 = get_password_hash("password123")
    assert hash1 != hash2
    assert len(hash1) > 0


@pytest.mark.asyncio
async def test_authenticate_user():
    mock_db = AsyncMock(spec=AsyncSession)
    mock_user = AsyncMock()
    mock_user.email = "test@example.com"
    mock_user.password = get_password_hash("password123")

    with patch(
        "src.services.auth.UserRepository.get_user_by_email", return_value=mock_user
    ) as mock_repo:
        user = await authenticate_user("test@example.com", "password123", mock_db)
        assert user is not False
        assert user.email == "test@example.com"

        user = await authenticate_user("test@example.com", "wrongpassword", mock_db)
        assert user is False

        mock_repo.assert_called_with("test@example.com")


def test_generate_email_verification_token():
    token = generate_email_verification_token()
    assert isinstance(token, str)
    assert len(token) > 0


def test_send_reset_password_email():
    with patch("smtplib.SMTP", autospec=True) as mock_smtp:
        mock_instance = MagicMock()
        mock_smtp.return_value.__enter__.return_value = mock_instance

        send_reset_password_email("test@example.com", "token123")

        # Генеруємо очікуваний текст листа
        expected_msg = MIMEText("Your password reset token is: token123")
        expected_msg['Subject'] = 'Password Reset'
        expected_msg['From'] = 'your_email@example.com'
        expected_msg['To'] = "test@example.com"

        mock_smtp.assert_called_once_with("smtp.example.com", 587)
        mock_instance.starttls.assert_called_once()
        mock_instance.login.assert_called_once_with("your_email@example.com", "your_password")
        mock_instance.sendmail.assert_called_once_with(
            "your_email@example.com",
            ["test@example.com"],
            expected_msg.as_string(),  # Враховуємо форматування MIMEText
        )