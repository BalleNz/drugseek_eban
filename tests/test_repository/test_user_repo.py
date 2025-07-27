import pytest

from database.models.user import User
from schemas import UserTelegramDataSchema, UserSchema


def get_user() -> User:
    """
    User model factory.
    """
    return User(
            telegram_id="1488221",
            first_name="Оззи",
            last_name="озборн",
            username="huesos",
        )


@pytest.mark.asyncio
async def test_get_from_telegram_data(user_service, user_repo):
    user_model = await user_repo.create(get_user())

    user_telegram_data: UserTelegramDataSchema = UserTelegramDataSchema.model_validate(user_model)

    user: UserSchema = await user_service.repo.get_or_create_from_telegram(user_telegram_data)
    assert user.telegram_id == "1488221"
    assert user.first_name == "Оззи"
    assert user.last_name == "озборн"
    assert user.username == "huesos"
    assert user.allowed_requests == 3


@pytest.mark.asyncio
async def test_create_from_telegram_data(user_service, user_repo):
    user_telegram_data = UserTelegramDataSchema.model_validate(get_user())

    user: UserSchema = await user_service.repo.get_or_create_from_telegram(user_telegram_data)

    assert user.telegram_id == "1488221"
    assert user.first_name == "Оззи"
    assert user.last_name == "озборн"
    assert user.username == "huesos"
    assert user.allowed_requests == 3

@pytest.mark.asyncio
async def test_get_by_telegram_id(user_service):
    user_model = await user_service.repo.create(get_user())

@pytest.mark.asyncio
async def test_allow_drug_to_user(user_service, drug_repo):
    ...

