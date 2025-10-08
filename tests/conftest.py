import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from drug_search.core.services.drug_service import DrugService
from drug_search.core.services.user_service import UserService
from drug_search.infrastructure.database.repository.drug_repo import DrugRepository
from drug_search.infrastructure.database.repository.user_repo import UserRepository


@pytest.fixture
def mock_session():
    """Создает мок асинхронной сессии"""
    session = AsyncMock(spec=AsyncSession)
    session.commit = AsyncMock()
    session.execute = AsyncMock()
    session.scalar = AsyncMock()
    session.scalars = AsyncMock()
    session.get = AsyncMock()
    session.add = AsyncMock()
    session.refresh = AsyncMock()
    session.rollback = AsyncMock()
    return session


@pytest.fixture
def mock_drug_repo(mock_session):
    """Создает мок репозитория препаратов"""
    repo = DrugRepository(session=mock_session)
    # Мокаем методы репозитория
    repo.create = AsyncMock()
    repo.get = AsyncMock()
    repo.delete = AsyncMock()
    repo.find_drug_by_query = AsyncMock()
    repo.get_with_all_relationships = AsyncMock()
    return repo


@pytest.fixture
def mock_user_repo(mock_session):
    """Создает мок репозитория пользователей"""
    repo = UserRepository(session=mock_session)
    # Мокаем методы репозитория
    repo.create = AsyncMock()
    repo.get = AsyncMock()
    repo.get_or_create_from_telegram = AsyncMock()
    repo.allow_drug_to_user = AsyncMock()
    repo.get_allowed_drug_names = AsyncMock()
    repo.update_user_description = AsyncMock()
    repo.increment_user_requests = AsyncMock()
    return repo


@pytest.fixture
def drug_service(mock_drug_repo):
    """Создает сервис препаратов с моком репозитория"""
    return DrugService(mock_drug_repo)


@pytest.fixture
def user_service(mock_user_repo):
    """Создает сервис пользователей с моком репозитория"""
    return UserService(mock_user_repo)


@pytest.fixture
def test_user_data():
    return {
        "telegram_id": "123456789",
        "username": "testuser",
        "first_name": "Test",
        "last_name": "User"
    }
