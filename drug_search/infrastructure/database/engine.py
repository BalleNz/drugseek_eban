from typing import Final, AsyncGenerator

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

from drug_search.config import config

DEBUG: Final[bool] = config.DEBUG
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
        connect_args={
            "server_settings": {
                "timezone": "UTC",  # Явно указываем UTC для каждого соединения
            }
        }
    )
    return engine, async_sessionmaker(engine, expire_on_commit=False)


engine, async_session_maker = create_async_db_engine_and_session(
    database_url=DATABASE_URL,
    echo=False,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800
)


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session_generator:
        try:
            yield session_generator
        except Exception:
            await session_generator.rollback()
            raise
        finally:
            await session_generator.close()
