import asyncio
from typing import AsyncGenerator
from pathlib import Path

import pytest
from alembic.config import Config
from alembic import command
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

from config import config


# Фикстура для event loop
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
async def test_engine():
    test_db_url = config.DATABASE_URL + "_test"

    test_engine = create_async_engine(
        test_db_url,
        echo=True,
        poolclass=NullPool,  # Используем NullPool для тестов
    )

    # Применяем миграции
    await apply_migrations(test_engine)

    print("\n" + "=" * 50)
    print("Применены миграции, созданы таблицы")
    print("=" * 50 + "\n")

    yield test_engine

    # Откатываем миграции
    await downgrade_migrations(test_engine)

    await test_engine.dispose()


async def apply_migrations(engine):
    """Применяем все миграции"""
    base_dir = Path(__file__).parent.parent
    alembic_ini_path = base_dir / "alembic.ini"
    alembic_dir = base_dir / "alembic"

    alembic_cfg = Config(str(alembic_ini_path))
    alembic_cfg.set_main_option("sqlalchemy.url", str(engine.url).replace("+asyncpg", ""))
    alembic_cfg.set_main_option("script_location", str(alembic_dir))

    async with engine.connect() as connection:
        def upgrade(conn):
            alembic_cfg.attributes['connection'] = conn
            command.upgrade(alembic_cfg, "head")

        await connection.run_sync(upgrade)


async def downgrade_migrations(engine):
    """Откатываем все миграции"""
    base_dir = Path(__file__).parent.parent
    alembic_ini_path = base_dir / "alembic.ini"
    alembic_dir = base_dir / "alembic"

    alembic_cfg = Config(str(alembic_ini_path))
    alembic_cfg.set_main_option("sqlalchemy.url", str(engine.url).replace("+asyncpg", ""))
    alembic_cfg.set_main_option("script_location", str(alembic_dir))

    async with engine.connect() as connection:
        def downgrade(conn):
            alembic_cfg.attributes['connection'] = conn
            command.downgrade(alembic_cfg, "base")

        await connection.run_sync(downgrade)


@pytest.fixture
async def session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    async with async_sessionmaker(
            test_engine,
            expire_on_commit=False,
            autoflush=False
    )() as test_session:
        try:
            yield test_session
        finally:
            await test_session.rollback()
            await test_session.close()