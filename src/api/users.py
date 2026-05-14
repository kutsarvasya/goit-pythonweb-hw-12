from fastapi import APIRouter, Depends, Request, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.db import get_db
from src.database.models import User
from src.schemas import UserResponse
from src.services.auth import get_current_user
from src.services.limiter import limiter
from src.conf.config import config
from src.repository.users import UserRepository

from src.services.upload_file import UploadFileService

router = APIRouter(prefix="/users", tags=["users"])


@router.get(
    "/me",
    response_model=UserResponse,
)
@limiter.limit("10/minute")
async def me(
    request: Request,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    return user


@router.patch(
    "/avatar",
    response_model=UserResponse,
)
async def update_avatar_user(
    file: UploadFile = File(),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    avatar_url = UploadFileService(
        config.CLD_NAME,
        config.CLD_API_KEY,
        config.CLD_API_SECRET,
    ).upload_file(
        file,
        user.username,
    )

    repo = UserRepository(db)

    updated_user = await repo.update_avatar_url(
        user.email,
        avatar_url,
    )

    return updated_user
