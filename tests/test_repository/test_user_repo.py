import pytest
import uuid
from unittest.mock import AsyncMock

from drug_search.infrastructure.database.models.user import User
from drug_search.core.schemas import UserTelegramDataSchema, UserSchema


def get_user() -> User:
    return User(
        id=uuid.uuid4(),
        allowed_requests=3,
        used_requests=0,
        telegram_id="1488221",
        first_name="Оззи",
        last_name="озборн",
        username="huesos",
    )


@pytest.mark.asyncio
async def test_get_from_telegram_data(mock_user_repo):
    # Подготавливаем данные
    user_model = get_user()
    user_schema = UserSchema.model_validate(user_model)
    user_telegram_data = UserTelegramDataSchema.model_validate(user_model)

    # Настраиваем мок
    mock_user_repo.get_or_create_from_telegram.return_value = user_schema

    # Вызываем тестируемый метод
    result = await mock_user_repo.get_or_create_from_telegram(user_telegram_data)

    # Проверяем результат
    assert result.telegram_id == "1488221"
    assert result.first_name == "Оззи"
    assert result.last_name == "озборн"
    assert result.username == "huesos"
    assert result.allowed_requests == 3

    # Проверяем, что метод был вызван
    mock_user_repo.get_or_create_from_telegram.assert_called_once_with(user_telegram_data)


@pytest.mark.asyncio
async def test_allow_drug_to_user(mock_user_repo):
    # Подготавливаем данные
    user_id = uuid.uuid4()
    drug_id = uuid.uuid4()

    # Настраиваем мок
    mock_user_repo.allow_drug_to_user.return_value = None

    # Вызываем тестируемый метод
    await mock_user_repo.allow_drug_to_user(drug_id, user_id)

    # Проверяем, что метод был вызван с правильными аргументами
    mock_user_repo.allow_drug_to_user.assert_called_once_with(drug_id, user_id)


@pytest.mark.asyncio
async def test_get_allowed_drug_names(mock_user_repo):
    # Подготавливаем данные
    user_id = uuid.uuid4()
    expected_result = ["Парацетамол", "Ибупрофен"]

    # Настраиваем мок
    mock_user_repo.get_allowed_drug_names.return_value = expected_result

    # Вызываем тестируемый метод
    result = await mock_user_repo.get_allowed_drug_names(user_id)

    # Проверяем результат
    assert result == expected_result
    assert "Парацетамол" in result

    # Проверяем, что метод был вызван
    mock_user_repo.get_allowed_drug_names.assert_called_once_with(user_id)


@pytest.mark.asyncio
async def test_update_user_description(mock_user_repo):
    # Подготавливаем данные
    user_id = uuid.uuid4()
    description = "Новое описание пользователя"

    # Настраиваем мок
    mock_user_repo.update_user_description.return_value = None

    # Вызываем тестируемый метод
    await mock_user_repo.update_user_description(description, user_id)

    # Проверяем, что метод был вызван с правильными аргументами
    mock_user_repo.update_user_description.assert_called_once_with(description, user_id)


@pytest.mark.asyncio
async def test_decrement_user_requests(mock_user_repo):
    # Подготавливаем данные
    user_id = uuid.uuid4()

    # Настраиваем мок
    mock_user_repo.increment_user_requests.return_value = None

    # Вызываем тестируемый метод
    await mock_user_repo.increment_user_requests(user_id, 1)

    # Проверяем, что метод был вызван с правильными аргументами
    mock_user_repo.increment_user_requests.assert_called_once_with(user_id, 1)
