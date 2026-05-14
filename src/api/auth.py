from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.email import send_email, send_reset_password_email

from src.database.db import get_db
from src.repository.users import UserRepository
from src.schemas import (
    Token,
    UserCreate,
    UserResponse,
    RequestEmail,
    RequestPasswordReset,
    ResetPassword,
)
from src.services.auth import (
    Hash,
    create_access_token,
    create_email_token,
    get_email_from_token,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
async def register_user(
    user_data: UserCreate,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user.

    Checks if the email or username already exists,
    hashes the password, creates a new user,
    and sends a verification email.

    Args:
        user_data: User registration data.
        background_tasks: FastAPI background tasks.
        request: HTTP request object.
        db: Database session.

    Returns:
        Created user object.
    """

    repo = UserRepository(db)

    email_user = await repo.get_user_by_email(user_data.email)
    if email_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists",
        )

    username_user = await repo.get_user_by_username(user_data.username)
    if username_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this username already exists",
        )

    hashed_password = Hash.get_password_hash(user_data.password)

    new_user = await repo.create_user(user_data, hashed_password)

    background_tasks.add_task(
        send_email,
        new_user.email,
        new_user.username,
        str(request.base_url),
    )

    return new_user


@router.post("/login", response_model=Token)
async def login_user(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    """
    Authenticate user and return JWT access token.

    Validates username and password,
    checks email confirmation status,
    and generates an access token.

    Args:
        form_data: OAuth2 login form.
        db: Database session.

    Returns:
        JWT access token.
    """

    repo = UserRepository(db)

    user = await repo.get_user_by_username(form_data.username)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not Hash.verify_password(
        form_data.password,
        user.hashed_password,
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email not confirmed",
        )

    access_token = await create_access_token(data={"sub": user.email})

    return {
        "access_token": access_token,
        "token_type": "bearer",
    }


@router.get("/confirmed_email/{token}")
async def confirmed_email(
    token: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Confirm user email address.

    Verifies the email token and updates
    the user confirmation status.

    Args:
        token: Email verification token.
        db: Database session.

    Returns:
        Confirmation message.
    """

    email = await get_email_from_token(token)

    repo = UserRepository(db)
    user = await repo.get_user_by_email(email)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification error",
        )

    if user.confirmed:
        return {"message": "Your email is already confirmed"}

    await repo.confirmed_email(email)

    return {"message": "Email confirmed successfully"}


@router.post("/request_email")
async def request_email(
    body: RequestEmail,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Send email confirmation message again.

    Checks user confirmation status and
    sends a new verification email.

    Args:
        body: User email request data.
        background_tasks: FastAPI background tasks.
        request: HTTP request object.
        db: Database session.

    Returns:
        Information message.
    """

    repo = UserRepository(db)
    user = await repo.get_user_by_email(body.email)

    if user is None:
        return {"message": "Check your email for confirmation"}

    if user.confirmed:
        return {"message": "Your email is already confirmed"}

    background_tasks.add_task(
        send_email,
        user.email,
        user.username,
        str(request.base_url),
    )

    return {"message": "Check your email for confirmation"}


@router.post("/request_password_reset")
async def request_password_reset(
    body: RequestPasswordReset,
    background_tasks: BackgroundTasks,
    request: Request,
    db: AsyncSession = Depends(get_db),
):
    """
    Send password reset email.

    Checks user existence and sends
    password reset link to email.

    Args:
        body: Password reset request data.
        background_tasks: FastAPI background tasks.
        request: HTTP request object.
        db: Database session.

    Returns:
        Information message.
    """

    repo = UserRepository(db)

    user = await repo.get_user_by_email(body.email)

    if user is None:
        return {"message": "Check your email for password reset"}

    background_tasks.add_task(
        send_reset_password_email,
        user.email,
        user.username,
        str(request.base_url),
    )

    return {"message": "Check your email for password reset"}


@router.post("/reset_password/{token}")
async def reset_password(
    token: str,
    body: ResetPassword,
    db: AsyncSession = Depends(get_db),
):
    """
    Reset user password.

    Verifies reset token and updates
    user password with new hashed password.

    Args:
        token: Password reset token.
        body: New password data.
        db: Database session.

    Returns:
        Success message.

    Raises:
        HTTPException: If user does not exist.
    """

    email = await get_email_from_token(token)

    repo = UserRepository(db)

    user = await repo.get_user_by_email(email)

    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    hashed_password = Hash.get_password_hash(body.password)

    await repo.update_password(
        email,
        hashed_password,
    )

    return {"message": "Password updated successfully"}
