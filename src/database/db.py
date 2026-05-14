import contextlib

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from src.conf.config import config


class DatabaseSessionManager:
    """
    Database session manager for asynchronous SQLAlchemy sessions.

    Creates database engine and session factory,
    handles session lifecycle and rollback operations.
    """

    def __init__(self, url: str):
        """
        Initialize database engine and session maker.

        Args:
            url: Database connection URL.
        """

        self._engine: AsyncEngine | None = create_async_engine(url)

        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False,
            autocommit=False,
            bind=self._engine,
        )

    @contextlib.asynccontextmanager
    async def session(self):
        """
        Create and manage asynchronous database session.

        Yields:
            Async database session.

        Raises:
            Exception: If session manager is not initialized.
            SQLAlchemyError: If database error occurs.
        """

        if self._session_maker is None:
            raise Exception("Database session is not initialized")

        session = self._session_maker()

        try:
            yield session

        except SQLAlchemyError as e:
            await session.rollback()
            raise

        finally:
            await session.close()


sessionmanager = DatabaseSessionManager(config.DB_URL)


async def get_db():
    """
    Dependency for getting database session.

    Yields:
        Async database session.
    """

    async with sessionmanager.session() as session:
        yield session
