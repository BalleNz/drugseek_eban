from typing import AsyncGenerator

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker

from config import config
from core.database.models.base import IDMixin
from core.database.models.drug import Drug  # Пример модели
from core.database.repository.drug import DrugRepository
from core.services.drug import DrugService


@pytest.fixture(scope="session")
async def test_engine():
    test_db_url = config.DATABASE_URL + "_test"

    test_engine = create_async_engine(
        test_db_url,
        echo=True,
        pool_size=5,
        max_overflow=5,
        pool_timeout=5,
        pool_recycle=5
    )

    async with test_engine.connect() as conn:
        # create tables from IDMixin
        async with conn.begin():
            await conn.run_sync(IDMixin.metadata.create_all)

        yield test_engine

        # delete tables after session
        async with conn.begin():
            await conn.run_sync(IDMixin.metadata.drop_all)

    # close test_engine
    await test_engine.dispose(close=True)


@pytest.fixture
async def session(test_engine) -> AsyncGenerator[AsyncSession, None]:
    async with async_sessionmaker(test_engine, expire_on_commit=False)() as test_session:
        yield test_session
        await test_session.rollback()
        await test_session.close()


@pytest.fixture
async def drug_repo(session: AsyncSession) -> DrugRepository:
    return DrugRepository(session=session)


@pytest.fixture
async def drug_service(drug_repo: DrugRepository):
    return DrugService(drug_repo)
