import secrets
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession
from email.mime.text import MIMEText
import smtplib

from src.conf.config import config
from src.repository.users import UserRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def create_access_token(data: dict, expires_delta: Optional[float] = None):
    """
    Create a new access token.

    Args:
        data (dict): The data to encode in the token.
        expires_delta (Optional[float], optional): The expiration time in minutes. Defaults to None.

    Returns:
        str: The encoded JWT token.

    Raises:
        None
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + timedelta(minutes=expires_delta)
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.SECRET_KEY, algorithm=config.ALGORITHM)
    return encoded_jwt

def verify_password(plain_password, hashed_password):
    """Verify that the plain text password matches the hashed password.

    Args:
        plain_password (str): The plain text password.
        hashed_password (str): The hashed password.

    Returns:
        bool: True if the passwords match, False otherwise.

    Raises:
        None
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    """Get the hash of the password.

    Args:
        password (str): The password.

    Returns:
        str: The hash of the password.

    Raises:
        None
    """
    return pwd_context.hash(password)

async def authenticate_user(email: str, password: str, db: AsyncSession):
    """Authenticate a user.

    Args:
        email (str): The email of the user.
        password (str): The password of the user.
        db (AsyncSession): The database session.

    Returns:
        User: The authenticated user.

    Raises:
        None
    """
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_email(email)

    if not user:
        return False

    if not verify_password(password, user.password):
        return False

    return user

def generate_email_verification_token():
    """
    Generate a random token for email verification.

    Returns:
        str: The generated token.
    """
    return secrets.token_urlsafe(32)

def send_reset_password_email(email: str, token: str):
    """
    Email the user with a password reset token.

    Args:
        email (str): The email address of the user.
        token (str): The password reset token.

    Returns:
        None

    """
    try:
        msg = MIMEText(f"Your password reset token is: {token}")
        msg['Subject'] = 'Password Reset'
        msg['From'] = 'your_email@example.com'
        msg['To'] = email

        with smtplib.SMTP('smtp.example.com', 587) as server:
            server.starttls()
            server.login('your_email@example.com', 'your_password')
            server.sendmail('your_email@example.com', [email], msg.as_string())
    except Exception as e:
        print(f"Failed to send email: {e}")