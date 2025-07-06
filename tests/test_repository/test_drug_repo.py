import pytest

from core.database.models.drug import Drug
from core.database.repository.drug import DrugRepository


@pytest.mark.asyncio
async def test_create_drug(drug_repo: DrugRepository, drug_model: Drug):
    model: Drug = await drug_repo.create(drug_model)

    assert model.dosages_fun_fact == "Test fact"

@pytest.mark.asyncio
async def test_update_drug_neuro(drug_repo, drug_model):
    await drug_repo.drug_update("железо")
