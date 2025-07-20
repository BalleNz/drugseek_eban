import pytest

from core.database.models.drug import Drug, DrugSynonym, DrugAnalog
from core.database.repository.drug import DrugRepository
from services.drug import DrugService


@pytest.mark.asyncio
async def test_create_drug(drug_repo: DrugRepository, drug_model: Drug):
    model: Drug = await drug_repo.create(drug_model)

    assert model.dosages_fun_fact == "Test fact"


@pytest.mark.asyncio
async def test_search_by_name(drug_repo: DrugRepository, drug_service: DrugService):
    """
    Тестирование записи препарата в БД, а после — поиска с использованием pg_trgm.

    check:
        - pg_trgm
    """
    drug_name_ru = "Парацетамол"
    search_query = "парамол"

    drug: Drug = await drug_service.create_drug(drug_name_ru)
    drug.analogs.append(DrugAnalog(analog_name="Ибупрофен", percent=50, difference="тебя ебать не должно"))
    drug.synonyms.append(DrugSynonym(drug_id=drug.id, synonym=drug_name_ru))
    drug = await drug_repo.save(drug)

    founded_drug = await drug_repo.find_drug_by_query(search_query)

    # Проверяем что нашли правильный синоним
    assert founded_drug is not None
    assert founded_drug.id == drug.id
    assert founded_drug.name == drug.name

    # проверка смежных таблиц
    assert founded_drug.analogs[0].analog_name == "Ибупрофен"


@pytest.mark.asyncio
async def test_update_dosages_and_analogs(drug_service, drug_repo):
    drug: Drug = await drug_service.create_drug("Acetaminophen")
    updated_drug = await drug_service.update_dosages(drug)

    assert updated_drug
    assert updated_drug.dosages_fun_fact
    assert updated_drug.excretion
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
async def test_update_pathways(drug_service, drug_repo):
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
async def test_update_combinations(drug_service, drug_repo):
    drug: Drug = await drug_service.create_drug("Primabolan")
    drug = await drug_service.update_combinations(drug)

    for combination in drug.combinations:
        assert combination.effect
        assert combination.combination_type
        if combination.combination_type == "bad":
            assert combination.risks
        assert combination.sources
        assert combination.substance
