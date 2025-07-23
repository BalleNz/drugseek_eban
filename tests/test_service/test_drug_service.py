import pytest

from database.models.drug import Drug
from services.drug import DrugService


@pytest.mark.asyncio
async def test_drug_create_drug(drug_service: DrugService, drug_model):
    await drug_service.create_drug(drug_model.name)


@pytest.mark.asyncio
async def test_update_dosages_and_analogs(drug_service):
    drug = await drug_service.create_drug("Acetaminophen")
    updated_drug = await drug_service.update_dosages(drug)

    assert updated_drug
    assert updated_drug.dosages_fun_fact
    assert updated_drug.elimination
    assert updated_drug.metabolism
    assert updated_drug.absorption

    for analog in updated_drug.analogs:
        assert analog.percent
        assert analog.difference
        assert analog.analog_name

    assert updated_drug.description
    assert updated_drug.classification
    assert updated_drug.latin_name


@pytest.mark.asyncio
async def test_update_pathways(drug_service):
    drug: Drug = await drug_service.create_drug("Acetaminophen")
    drug = await drug_service.update_pathways(drug)

    assert drug.pathways
    assert drug.pathways[0].effect
    assert drug.pathways[0].pathway
    assert drug.pathways[0].activation_type
    assert drug.pathways[0].binding_affinity
    assert drug.pathways[0].affinity_description
    assert drug.pathways[0].receptor


@pytest.mark.asyncio
async def test_update_combinations(drug_service):
    drug: Drug = await drug_service.create_drug("Primabolan")
    drug = await drug_service.update_combinations(drug)

    for combination in drug.combinations:
        assert combination.effect
        assert combination.combination_type
        if combination.combination_type == "bad":
            assert combination.risks
        assert combination.sources
        assert combination.substance
