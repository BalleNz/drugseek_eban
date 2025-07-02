from contextlib import asynccontextmanager
from typing import Final

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from config import config

DEBUG_MODE: Final[bool] = config.DEBUG_MODE
DATABASE_URL: Final[str] = config.DATABASE_URL


def create_async_db_engine_and_session(
        database_url: str,
        echo: bool,
        pool_size: int,
        max_overflow: int,
        pool_timeout: int,
        pool_recycle: int,
):
    engine = create_async_engine(
        url=database_url,
        echo=echo,
        pool_size=pool_size,
        max_overflow=max_overflow,
        pool_timeout=pool_timeout,
        pool_recycle=pool_recycle,
    )
    return engine, async_sessionmaker(engine, expire_on_commit=False)


engine, async_session_maker = create_async_db_engine_and_session(
    database_url=DATABASE_URL,
    echo=True if DEBUG_MODE else False,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800
)


@asynccontextmanager
async def get_async_session():
    async with async_session_maker() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
