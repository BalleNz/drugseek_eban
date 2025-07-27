import pytest

from assistant import assistant
from core.database.models.drug import Drug, DrugSynonym


@pytest.mark.asyncio
async def test_update_dosages_and_analogs(drug_service):
    """
    Тестирование обновления данных о дозировках, аналогах, базовой информации препарата и синонимах для триграмм.
    """
    drug_model = Drug(
        name="Acetaminophen",
        name_ru="Парацетамол",
        synonyms=[
            DrugSynonym(
                synonym="Парацетамол"
            )
        ]
    )

    drug = await drug_service.repo.create(drug_model)

    assistant_response = assistant.get_dosage(drug.name)
    await drug_service.repo.update_dosages(drug.id, assistant_response=assistant_response)

    assert drug_model
    assert drug_model.dosages_fun_fact
    assert drug_model.elimination
    assert drug_model.metabolism
    assert drug_model.absorption

    for synonym in drug_model.synonyms:
        assert synonym.synonym

    for analog in drug_model.analogs:
        assert analog.percent
        assert analog.difference
        assert analog.analog_name

    for dosage in drug_model.dosages:
        assert dosage.route
        assert dosage.drug_id == drug.id
        ...

    assert drug_model.description
    assert drug_model.classification
    assert drug_model.latin_name


@pytest.mark.asyncio
async def test_update_pathways(drug_service):
    """
    Тестирование обновления путей активации препарата.
    """
    drug_model = Drug(
        name="Acetaminophen",
        name_ru="Парацетамол",
        synonyms=[
            DrugSynonym(
                synonym="Парацетамол"
            )
        ]
    )
    drug = await drug_service.repo.create(drug_model)

    assistant_response = assistant.get_pathways(drug_name=drug.name)
    await drug_service.repo.update_pathways(drug.id, assistant_response)

    assert drug_model.pathways
    for pathway in drug_model.pathways:
        assert pathway.effect
        assert pathway.pathway
        assert pathway.activation_type
        assert pathway.binding_affinity
        assert pathway.affinity_description
        assert pathway.receptor
        assert pathway.source


@pytest.mark.asyncio
async def test_update_combinations(drug_service):
    """
    Тестирование обновления комбинаций препарата.
    """
    drug_model = Drug(
        name="Acetaminophen",
        name_ru="Парацетамол",
        synonyms=[
            DrugSynonym(
                synonym="Парацетамол"
            )
        ]
    )
    drug = await drug_service.repo.create(drug_model)

    assistant_response = assistant.get_combinations(drug.name)
    await drug_service.repo.update_combinations(
        drug_id=drug.id,
        assistant_response=assistant_response
    )

    for combination in drug_model.combinations:
        assert combination.effect
        assert combination.combination_type
        if combination.combination_type == "bad":
            assert combination.risks
        assert combination.sources
        assert combination.substance
