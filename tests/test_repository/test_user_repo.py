import pytest

from drug_search.core.database.models.user import User
from drug_search.core.schemas import UserTelegramDataSchema, UserSchema
from test_repository.test_drug_repo import create_test_drug_model


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
async def test_get_from_telegram_data(user_repo):
    user_model = await user_repo.create(get_user())

    user_telegram_data: UserTelegramDataSchema = UserTelegramDataSchema.model_validate(user_model)

    user: UserSchema = await user_repo.get_or_create_from_telegram(user_telegram_data)
    assert user.telegram_id == "1488221"
    assert user.first_name == "Оззи"
    assert user.last_name == "озборн"
    assert user.username == "huesos"
    assert user.allowed_requests == 3


@pytest.mark.asyncio
async def test_create_from_telegram_data(user_repo):
    user_telegram_data = UserTelegramDataSchema.model_validate(get_user())

    user: UserSchema = await user_repo.get_or_create_from_telegram(user_telegram_data)

    assert user.telegram_id == "1488221"
    assert user.first_name == "Оззи"
    assert user.last_name == "озборн"
    assert user.username == "huesos"
    assert user.allowed_requests == 3


@pytest.mark.asyncio
async def test_get_by_telegram_id(user_repo):
    await user_repo.create(get_user())

    user = await user_repo.get_by_telegram_id(get_user().telegram_id)
    assert user.telegram_id == "1488221"
    assert user.first_name == "Оззи"
    assert user.last_name == "озборн"
    assert user.username == "huesos"
    assert user.allowed_requests == 3


@pytest.mark.asyncio
async def test_allow_drug_to_user(user_repo, drug_repo):
    drug = create_test_drug_model()
    drug_ = await drug_repo.create(drug)

    user: User = get_user()
    user = await user_repo.create(user)

    await user_repo.allow_drug_to_user(drug_.id, user.id)

    await user_repo._session.refresh(user)

    assert drug_.id in user.allowed_drug_ids


@pytest.mark.asyncio
async def test_get_allowed_drug_names(user_repo, drug_repo):
    drug = create_test_drug_model()
    drug_ = await drug_repo.create(drug)

    user: User = get_user()
    user = await user_repo.create(user)

    await user_repo.allow_drug_to_user(drug_.id, user.id)

    allowed_drug_names = await user_repo.get_allowed_drug_names(user.id)

    assert drug_.name_ru in allowed_drug_names


@pytest.mark.asyncio
async def test_get_allowed_drug_ids(user_repo, drug_repo):
    drug = create_test_drug_model()
    drug_ = await drug_repo.create(drug)

    user: User = get_user()
    user = await user_repo.create(user)

    await user_repo.allow_drug_to_user(drug_.id, user.id)

    allowed_drug_ids = await user_repo.get_allowed_drug_ids(user.id)

    assert drug.id in allowed_drug_ids


@pytest.mark.asyncio
async def test_update_description_without_Assistant(user_repo):
    """Тест обновления описание без ассистента."""
    user: User = get_user()
    user = await user_repo.create(user)

    description = "хуесос пидор лох какашка"

    await user_repo.update_user_description(description, user.id)

    await user_repo._session.refresh(user)

    assert user.description == description


@pytest.mark.asyncio
async def test_reduce_allowed_requests(user_repo, user = get_user()):
    user = await user_repo.create(user)
    assert user.allowed_requests == 3

    await user_repo.decrement_user_requests(user.id, 1)

    user = await user_repo.get(user.id)
    assert user.allowed_requests == 2

    await user_repo.decrement_user_requests(user.id, 2)
    assert user.allowed_requests == 0

