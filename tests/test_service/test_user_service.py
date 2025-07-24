import pytest

from database.models.user import User
from schemas import UserSchema, UserTelegramDataSchema


@pytest.mark.asyncio
async def test_get_or_create_from_telegram(user_service, user_repo):
    user_model = await user_repo.create(
        User(
            telegram_id="1488221",
            first_name="Оззи",
            last_name="озборн",
            username="huesos",
        )
    )

    user_telegram_data: UserTelegramDataSchema = UserTelegramDataSchema.model_validate(user_model)

    user: UserSchema = await user_service.get_or_create_from_telegram(user_telegram_data)

    assert user.telegram_id == "1488221"