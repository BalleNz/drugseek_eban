import asyncio
from typing import AsyncGenerator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.pool import NullPool

import app
from drug_search.config import config
from drug_search.infrastructure.database.repository.drug_repo import DrugRepository  # Писать везде АБСОЛЮТНЫЕ ПУТИ обязательно.
from drug_search.infrastructure.database.repository.user_repo import UserRepository
from drug_search.core.services.drug_service import DrugService
from drug_search.core.services.user_service import UserService


# Фикстура для event loop
@pytest.fixture(scope="session")
def event_loop():
    loop = asyncio.get_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session")
def client():
    with TestClient(app.fastapi_app) as c:
        yield c


@pytest.fixture(scope="session")
async def test_engine():
    test_db_url = config.DATABASE_URL_TEST

    test_engine = create_async_engine(
        test_db_url,
        echo=True,
        poolclass=NullPool,  # Используем NullPool для тестов
    )

    yield test_engine

    await test_engine.dispose()


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

            # Очищаем все таблицы. Важно.
            async with test_engine.begin() as conn:
                await conn.run_sync(lambda sync_conn: sync_conn.execute(text("TRUNCATE TABLE users, drugs CASCADE")))

            await test_session.close()


@pytest.fixture
async def drug_repo(session: AsyncSession) -> DrugRepository:
    async with session as session:
        return DrugRepository(session=session)


@pytest.fixture
async def drug_service(drug_repo: DrugRepository):
    return DrugService(drug_repo)


@pytest.fixture
async def user_repo(session: AsyncSession) -> UserRepository:
    return UserRepository(session=session)


@pytest.fixture
async def user_service(user_repo: UserRepository) -> UserService:
    return UserService(user_repo)


@pytest.fixture
def test_user_data():
    return {
        "telegram_id": "123456789",
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User",
        "photo_url": "https://example.com/photo.jpg"
    }


@pytest.fixture
async def auth_token(test_user_data, client):
    response = client.post("/v1/auth/", json=test_user_data)
    return response.json()["token"]

# TODO: перейти на моки
