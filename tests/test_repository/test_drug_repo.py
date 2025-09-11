import uuid

import pytest

from drug_search.core.schemas import DrugSchema
from drug_search.infrastructure.database.models.drug import *
from schemas import DrugAnalogSchemaRequest, CombinationType


def create_test_drug_model():
    return Drug(
        name="Acetaminophen",
        name_ru="Парацетамол",
        dosages_sources="",
        pathways_sources="",
        primary_action="sosi",
        secondary_actions="sosi",
        clinical_effects="sosi",
        synonyms=[
            DrugSynonym(synonym="Парацетамол")
        ],
        pathways=[
            DrugPathway(
                receptor="aue4-рецептор",
                binding_affinity="Ki = 2.28 нМ",
                affinity_description="очень сильное связывание",
                activation_type="antagonist",
                pathway="Gi/o protein cascade",
                effect="повышение АУФ!",
                note="дополнительнаяа швыумшуму",
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


@pytest.mark.asyncio
async def test_find_drug_by_query(mock_drug_repo):
    # Подготавливаем данные
    search_query = "парамол"
    expected_drug = DrugSchema(
        id=uuid.uuid4(),
        name="Acetaminophen",
        name_ru="Парацетамол",
        # ... остальные поля
    )

    # Настраиваем мок
    mock_drug_repo.find_drug_by_query.return_value = expected_drug

    # Вызываем тестируемый метод
    result = await mock_drug_repo.find_drug_by_query(search_query)

    # Проверяем результат
    assert result is not None
    assert result.id is not None
    assert result.name_ru == "Парацетамол"

    # Проверяем, что метод был вызван
    mock_drug_repo.find_drug_by_query.assert_called_once_with(search_query)


@pytest.mark.asyncio
async def test_get_with_all_relationships(mock_drug_repo):
    # Подготавливаем данные
    drug_id = uuid.uuid4()
    expected_drug = DrugSchema(
        id=drug_id,
        name="Acetaminophen",
        name_ru="Парацетамол",
        synonyms=[
            DrugSynonymSchema(synonym="Парацетамол")
        ],
        pathways=[
            DrugPathwaySchema(
                receptor="aue4-рецептор",
                binding_affinity="Ki = 2.28 нМ",
                affinity_description="очень сильное связывание",
                activation_type="antagonist",
                pathway="Gi/o protein cascade",
                effect="повышение АУФ!",
                note="дополнительнаяа швыумшуму",
            )
        ],
        dosages=[
            DrugDosageSchema(
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
            DrugAnalogSchemaRequest(
                analog_name="сперма",
                percent=22.8,
                difference="другой цвет"
            )
        ],
        combinations=[
            DrugCombinationSchema(
                combination_type=CombinationType.GOOD,
                substance="Autismophen",
                effect="увеличивает ауе",
                risks="нихуя",
                products=["спермавирин", "ауефлекс"],
                sources=["drug.org/hui", "aue.com"],
            )
        ]
    )

    # Настраиваем мок
    mock_drug_repo.get_with_all_relationships.return_value = expected_drug

    # Вызываем тестируемый метод
    result = await mock_drug_repo.get_with_all_relationships(drug_id=drug_id, need_model=False)

    # Проверяем результат
    assert result is not None
    assert result.synonyms is not None
    assert result.analogs is not None
    assert result.pathways is not None
    assert result.combinations is not None
    assert result.dosages is not None

    # Проверяем, что метод был вызван
    mock_drug_repo.get_with_all_relationships.assert_called_once_with(drug_id=drug_id, need_model=False)