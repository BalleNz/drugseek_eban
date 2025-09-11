import pytest

from drug_search.infrastructure.database.models.drug import Drug, DrugSynonym
from drug_search.core.schemas import DrugSchema
from test_repository.test_drug_repo import create_test_drug_model


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
        name="Drostanalone",
        name_ru="Парацетамол",
        synonyms=[
            DrugSynonym(
                synonym="Парацетамол"
            )
        ]
    )
    drug = await drug_service.repo.create(drug_model)

    assistant_response = assistant.get_synergists(drug.name)
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


@pytest.mark.asyncio
async def test_update_researches(drug_service, drug_repo):
    drug = create_test_drug_model()
    drug = await drug_repo.create(drug)

    await drug_service.update_drug_researches(drug_id=drug.id, drug_name=drug.name)

    refreshed_drug: DrugSchema = await drug_repo.get_with_all_relationships(drug.id)

    for research in refreshed_drug.researches:
        assert research.interest
        assert research.authors
        assert research.description
        assert research.doi
        assert research.name
        assert research.date
        assert research.url
        assert research.summary
        assert research.study_type
        assert research.journal
