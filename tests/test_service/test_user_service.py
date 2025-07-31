import uuid

import pytest

from test_repository.test_drug_repo import create_test_drug_model
from test_repository.test_user_repo import get_user


@pytest.mark.asyncio
async def test_get_user_description_via_assistant(user_service, drug_repo):
    user = get_user()
    await user_service.repo.create(user)
    await user_service.repo._session.refresh(user)

    # добавление препаратов
    drug_names_ru = [
        "роаккутан",
        "теанин",
        "Тренболон",
        "Тестостерон",
        "ук11",
        "тадалафил",
        "виагра",
        "кленбутерол",
    ]
    drugs = [create_test_drug_model() for _ in range(8)]
    for drug in drugs:
        drug.name_ru = drug_names_ru.pop()

        drug.name = str(uuid.uuid4())  # to evade unique field
        drug.analogs = []
        drug.pathways = []
        drug.synonyms = []
        drug.combinations = []

        await drug_repo.create(drug)
        await user_service.allow_drug_to_user(user_id=user.id, drug_id=drug.id)

    await user_service.update_user_description(user.id)
    await user_service.repo._session.refresh(user)

    assert user.description

