import pytest

from core.database.models.drug import Drug
from core.database.repository.drug import DrugRepository


@pytest.mark.asyncio
async def test_create_drug(drug_repo: DrugRepository, drug_model: Drug):
    model: Drug = await drug_repo.create(drug_model)

    assert model.fun_fact == "Test fact"
