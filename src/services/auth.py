from datetime import datetime, timedelta, UTC
from typing import Optional

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
    @staticmethod
    def verify_password(
        plain_password,
        hashed_password,
    ):
        return pwd_context.verify(
            plain_password,
            hashed_password,
        )

    @staticmethod
    def get_password_hash(password: str):
        return pwd_context.hash(password)


async def create_access_token(
    data: dict,
    expires_delta: Optional[int] = None,
):
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

    repo = UserRepository(db)

    user = await repo.get_user_by_email(email)

    if user is None:
        raise credentials_exception

    return user


async def create_email_token(data: dict):
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
