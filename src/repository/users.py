from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.models import User
from src.schemas import UserCreate


class UserRepository:
    """
    Repository for user database operations.

    Provides methods for user creation,
    authentication queries, email confirmation,
    and avatar updates.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize user repository.

        Args:
            session: Async database session.
        """

        self.db = session

    async def get_user_by_email(self, email: str) -> User | None:
        """
        Retrieve user by email address.

        Args:
            email: User email address.

        Returns:
            User object if found, otherwise None.
        """

        stmt = select(User).filter_by(email=email)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def get_user_by_username(self, username: str) -> User | None:
        """
        Retrieve user by username.

        Args:
            username: Username string.

        Returns:
            User object if found, otherwise None.
        """

        stmt = select(User).filter_by(username=username)
        result = await self.db.execute(stmt)
        return result.scalar_one_or_none()

    async def create_user(
        self,
        body: UserCreate,
        hashed_password: str,
    ) -> User:
        """
        Create a new user.

        Args:
            body: User registration data.
            hashed_password: Hashed user password.

        Returns:
            Created user object.
        """

        user = User(
            username=body.username,
            email=body.email,
            hashed_password=hashed_password,
        )

        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def confirmed_email(self, email: str) -> None:
        """
        Confirm user email address.

        Updates user confirmation status.

        Args:
            email: User email address.
        """

        user = await self.get_user_by_email(email)

        if user:
            user.confirmed = True
            await self.db.commit()

    async def update_avatar_url(
        self,
        email: str,
        url: str,
    ) -> User | None:
        """
        Update user avatar URL.

        Args:
            email: User email address.
            url: Avatar image URL.

        Returns:
            Updated user object if found, otherwise None.
        """

        user = await self.get_user_by_email(email)

        if user is None:
            return None

        user.avatar = url

        await self.db.commit()
        await self.db.refresh(user)

        return user

    async def update_password(
        self,
        email: str,
        hashed_password: str,
    ) -> User | None:
        """
        Update user password.

        Finds user by email and updates
        stored hashed password.

        Args:
            email: User email address.
            hashed_password: New hashed password.

        Returns:
            Updated user object if found, otherwise None.
        """

        user = await self.get_user_by_email(email)

        if user is None:
            return None

        user.hashed_password = hashed_password

        await self.db.commit()
        await self.db.refresh(user)

        return user
