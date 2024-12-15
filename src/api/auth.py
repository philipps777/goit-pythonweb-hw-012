import cloudinary
import cloudinary.uploader
from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File, BackgroundTasks
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from email_validator import validate_email, EmailNotValidError
from src.conf.config import config
from src.database.db import get_db
from src.database.models import User, Role
from src.schemas.user import UserResponse, UserCreate, TokenSchema, UserLogin, PasswordResetRequest, PasswordReset
from src.services.auth import (
    create_access_token,
    get_password_hash,
    authenticate_user,
    generate_email_verification_token,
    send_reset_password_email
)
from src.repository.users import UserRepository
from src.services.cache import CacheService

cloudinary.config(
    cloud_name=config.CLOUDINARY_CLOUD_NAME,
    api_key=config.CLOUDINARY_API_KEY,
    api_secret=config.CLOUDINARY_API_SECRET
)

router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
cache_service = CacheService()

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    """
        Get the current user based on the provided token.

        Args:
            token (str): The JWT token.
            db (AsyncSession): The database session.

        Returns:
            User: The current user.

        Raises:
            HTTPException: If the token is invalid or the user is not found.
        """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, config.SECRET_KEY, algorithms=[config.ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_email(email)
    if user is None:
        raise credentials_exception

    await cache_service.set(f"user:{user.id}", user.json(), ex=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60)

    return user

async def get_current_admin(current_user: User = Depends(get_current_user)):
    """
        Get the current admin user.

        Args:
            current_user (User): The current user.

        Returns:
            User: The current admin user.

        Raises:
            HTTPException: If the user is not an admin.
        """
    if current_user.role != Role.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions"
        )
    return current_user

@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register_user(body: UserCreate, db: AsyncSession = Depends(get_db)):
    """
        Register a new user.

        Args:
            body (UserCreate): The user registration data.
            db (AsyncSession): The database session.

        Returns:
            UserResponse: The created user.

        Raises:
            HTTPException: If the user already exists.
        """
    user_repo = UserRepository(db)

    existing_user = await user_repo.get_user_by_email(body.email)
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )

    hashed_password = get_password_hash(body.password)

    user = await user_repo.create_user(body, hashed_password)

    return UserResponse(
        id=user.id,
        username=user.username,
        email=user.email,
        role=user.role
    )

@router.post("/login", response_model=TokenSchema)
async def login(
        form_data: OAuth2PasswordRequestForm = Depends(),
        db: AsyncSession = Depends(get_db)
):
    """
        Log in a user.

        Args:
            form_data (OAuth2PasswordRequestForm): The login form data.
            db (AsyncSession): The database session.

        Returns:
            TokenSchema: The access and refresh tokens.

        Raises:
            HTTPException: If the username or password is incorrect.
        """
    user = await authenticate_user(form_data.username, form_data.password, db)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"sub": user.email},
        expires_delta=config.ACCESS_TOKEN_EXPIRE_MINUTES
    )

    refresh_token = create_access_token(
        data={"sub": user.email},
        expires_delta=config.REFRESH_TOKEN_EXPIRE_MINUTES
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/upload-avatar", response_model=UserResponse)
async def upload_avatar(
        file: UploadFile = File(...),
        current_user: User = Depends(get_current_user),
        db: AsyncSession = Depends(get_db)
):
    result = cloudinary.uploader.upload(file.file, folder="avatars")

    current_user.avatar = result['secure_url']
    await db.commit()

    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        avatar=current_user.avatar,
        role=current_user.role
    )

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: User = Depends(get_current_user)):
    """
        Get the current user's information.

        Args:
            current_user (User): The current user.

        Returns:
            UserResponse: The current user's information.
        """
    return UserResponse(
        id=current_user.id,
        username=current_user.username,
        email=current_user.email,
        avatar=current_user.avatar,
        role=current_user.role
    )

@router.post("/request-reset-password", response_model=dict)
async def request_reset_password(body: PasswordResetRequest, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    """
        Request a password reset.

        Args:
            body (PasswordResetRequest): The password reset request data.
            background_tasks (BackgroundTasks): The background tasks.
            db (AsyncSession): The database session.

        Returns:
            dict: A message indicating that the password reset email has been sent.

        Raises:
            HTTPException: If the user is not found.
        """
    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_email(body.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    token = generate_email_verification_token()
    await cache_service.set(f"reset_token:{token}", user.email, ex=config.ACCESS_TOKEN_EXPIRE_MINUTES * 60)

    background_tasks.add_task(send_reset_password_email, body.email, token)

    return {"msg": "Password reset email sent"}

@router.post("/reset-password", response_model=dict)
async def reset_password(body: PasswordReset, db: AsyncSession = Depends(get_db)):
    """
        Reset the user's password.

        Args:
            body (PasswordReset): The password reset data.
            db (AsyncSession): The database session.

        Returns:
            dict: A message indicating that the password has been reset.

        Raises:
            HTTPException: If the token is invalid or expired, or if the user is not found.
        """
    email = await cache_service.get(f"reset_token:{body.token}")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired token"
        )

    user_repo = UserRepository(db)
    user = await user_repo.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    hashed_password = get_password_hash(body.new_password)
    user.password = hashed_password
    await db.commit()

    await cache_service.delete(f"reset_token:{body.token}")

    return {"msg": "Password has been reset"}
