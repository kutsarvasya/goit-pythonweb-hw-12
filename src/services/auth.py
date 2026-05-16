from datetime import datetime, timedelta, UTC
from typing import Optional
from src.services.redis_cache import get_cache, set_cache

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf.config import config
from src.database.db import get_db
from src.repository.users import UserRepository

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class Hash:
    """
    Password hashing utility.

    Provides methods for hashing plain passwords
    and verifying passwords against stored hashes.
    """

    @staticmethod
    def verify_password(
        plain_password,
        hashed_password,
    ):
        """
        Verify plain password against hashed password.

        Args:
            plain_password: Password entered by user.
            hashed_password: Password hash stored in database.

        Returns:
            True if password is valid, otherwise False.
        """

        return pwd_context.verify(
            plain_password,
            hashed_password,
        )

    @staticmethod
    def get_password_hash(password: str):
        """
        Generate password hash.

        Args:
            password: Plain user password.

        Returns:
            Hashed password string.
        """

        return pwd_context.hash(password)


async def create_access_token(
    data: dict,
    expires_delta: Optional[int] = None,
):
    """
    Create JWT access token.

    Args:
        data: Payload data to encode into token.
        expires_delta: Optional token lifetime in seconds.

    Returns:
        Encoded JWT access token.
    """

    to_encode = data.copy()

    if expires_delta:
        expire = datetime.now(UTC) + timedelta(seconds=expires_delta)
    else:
        expire = datetime.now(UTC) + timedelta(seconds=config.JWT_EXPIRATION_SECONDS)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(
        to_encode,
        config.JWT_SECRET,
        algorithm=config.JWT_ALGORITHM,
    )

    return encoded_jwt


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db),
):
    """
    Retrieve current authenticated user from JWT token.

    Decodes access token, extracts user email,
    and loads user from cache or database.

    Args:
        token: JWT access token from Authorization header.
        db: Database session.

    Returns:
        Current authenticated user.

    Raises:
        HTTPException: If token is invalid or user does not exist.
    """

    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            config.JWT_SECRET,
            algorithms=[config.JWT_ALGORITHM],
        )

        email = payload["sub"]

        if email is None:
            raise credentials_exception

    except JWTError:
        raise credentials_exception

    cache_key = f"user:{email}"

    cached_user = await get_cache(cache_key)

    if cached_user:
        print("USER FROM REDIS")
        return cached_user

    print("USER FROM DATABASE")
    repo = UserRepository(db)

    user = await repo.get_user_by_email(email)

    if user is None:
        raise credentials_exception

    await set_cache(cache_key, user)

    return user


async def create_email_token(data: dict):
    """
    Create email verification token.

    Args:
        data: Payload data containing user email.

    Returns:
        Encoded JWT email verification token.
    """

    to_encode = data.copy()

    expire = datetime.now(UTC) + timedelta(days=7)
    to_encode.update({"iat": datetime.now(UTC), "exp": expire})

    token = jwt.encode(
        to_encode,
        config.JWT_SECRET,
        algorithm=config.JWT_ALGORITHM,
    )

    return token


async def get_email_from_token(token: str):
    """
    Extract email from verification token.

    Args:
        token: Email verification JWT token.

    Returns:
        Email address stored in token.

    Raises:
        HTTPException: If token is invalid.
    """

    try:
        payload = jwt.decode(
            token,
            config.JWT_SECRET,
            algorithms=[config.JWT_ALGORITHM],
        )
        email = payload["sub"]
        return email

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid token for email verification",
        )


class RoleChecker:
    """
    Dependency for checking user roles.

    Allows access only to users with permitted roles.
    """

    def __init__(self, allowed_roles: list):
        """
        Initialize role checker.

        Args:
            allowed_roles: List of roles allowed to access endpoint.
        """

        self.allowed_roles = allowed_roles

    async def __call__(
        self,
        user=Depends(get_current_user),
    ):
        """
        Check current user role.

        Args:
            user: Current authenticated user.

        Returns:
            Current user if role is allowed.

        Raises:
            HTTPException: If user role is not allowed.
        """

        if user.role not in self.allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Operation forbidden",
            )

        return user
