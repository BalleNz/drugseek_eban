
import pytest

from sqlalchemy import text
from core.database.models.drug import Drug, DrugSynonym
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
    search_query = "Парацетамол"

    drug: Drug = await drug_service.create_drug(search_query)
    drug.synonyms.append(DrugSynonym(drug_id=drug.id, synonym="Парацетамол"))
    drug = await drug_repo.save(drug)

    founded_drug = await drug_repo.find_drug_by_query(search_query)

    # Проверяем что нашли правильный синоним
    assert founded_drug is not None
    assert founded_drug.id == drug.id
    assert founded_drug.name == drug.name


@pytest.mark.asyncio
async def test_update_drug(drug_service, drug_repo):
    drug = await drug_service.update_dosages("роаккутан")

    drug_from_db: Drug = await drug_repo.get(drug.id)
    assert drug_from_db
    assert drug_from_db.dosages_fun_fact
    assert drug_from_db.excretion
    assert drug_from_db.metabolism
    assert drug_from_db.absorption
    assert drug_from_db.analogs

    assert drug_from_db.pathways[0].pathway
    assert drug_from_db.pathways[0].effect
    assert drug_from_db.clinical_effects
    assert drug_from_db.description
    assert drug_from_db.primary_action
