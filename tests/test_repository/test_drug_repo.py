import pytest

from conftest import drug_service, session
from core.database.models.drug import Drug, DrugSynonym, DrugPathway, DrugDosage, DrugAnalog, DrugCombination
from core.database.repository.drug import DrugRepository
from services.drug import DrugService


@pytest.mark.asyncio
async def test_search_by_name(drug_repo: DrugRepository, drug_service: DrugService):
    """
    Тестирование записи препарата в БД, а после — поиска с использованием pg_trgm.

    check:
        - pg_trgm
    """
    search_query = "парамол"

    await drug_repo.create(
        Drug(
            name="Acetaminophen",
            name_ru="Парацетамол",
            synonyms=[
                DrugSynonym(
                    synonym="Парацетамол"
                )
            ]
        )
    )

    founded_drug = await drug_repo.find_drug_by_query(search_query)

    # Проверяем что нашли правильный синоним
    assert founded_drug is not None
    assert founded_drug.id
    assert founded_drug.name_ru


@pytest.mark.asyncio
async def test_get_relationships(drug_repo: DrugRepository):
    drug: Drug = await drug_repo.create(
        Drug(
            name="Acetaminophen",
            name_ru="Парацетамол",
            synonyms=[
                DrugSynonym(
                    synonym="Парацетамол"
                )
            ],
            pathways=[
                DrugPathway(
                    receptor="aue4-рецептор",
                    binding_affinity="Ki = 2.28 нМ",
                    affinity_description="очень сильное связывание",
                    activation_type="antagonist",
                    pathway="Gi/o protein cascade",
                    effect="повышение АУФ!",
                    source="drugbank.com",
                    note="дополнительнаяа швыумшуму"
                )
            ],
            dosages=[
                DrugDosage(
                    route="other",
                    method="peroral",
                    per_time="500 мг",
                    max_day="2000 мг",
                    per_time_weight_based="20мг на 1 кг",
                    max_day_weight_based="50мг на 1 кг",
                    onset="немедленно",
                    half_life="3 часа",
                    duration="12 часов",
                    notes="хуй",
                )
            ],
            analogs=[
                DrugAnalog(
                    analog_name="сперма",
                    percent=22.8,
                    difference="другой цвет"
                )
            ],
            combinations=[
            DrugCombination(
                combination_type="good",
                substance="Autismophen",
                effect="увеличивает ауе",
                risks="нихуя",
                products=["спермавирин", "ауефлекс"],
                sources=["drug.org/hui", "aue.com"],
            )
        ],
        )
    )

    drug: Drug = await drug_repo.get_with_all_relationships(drug_id=drug.id)
    assert drug.synonyms[0].synonym
    assert drug.analogs[0].percent
    assert drug.pathways[0].binding_affinity
    assert drug.combinations[0].effect
    assert drug.dosages[0].per_time
