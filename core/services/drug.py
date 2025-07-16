import logging
import uuid
from datetime import datetime
from typing import Optional

from core.database.models.drug import Drug, DrugDosage, DrugPathway, DrugCombination, DrugSynonym, DrugAnalog
from core.database.repository.drug import DrugRepository
from core.exceptions import DrugNotFound
from exceptions import AssistantResponseError
from neuro_assistant.assistant import assistant
from schemas.drug import AssistantResponseCombinations

logger = logging.getLogger("bot.core.drug_service")


class DrugService:
    def __init__(self, repo: DrugRepository):
        self.repo = repo

    async def get_drug(self, user: ..., user_query: str) -> Optional[Drug]:
        """
        Возвращает препарат по запросу юзера.

        - поиск препаратов по имени в таблице синонимов на русском.
        """



        drug: Drug = await self.repo.get_drug_by_user_query(user_query=user_query)
        if drug:
            # TODO: if drug.id in user.allowed_drugs: return drug; else return None
            return drug
        return None  # Далее будет обработка на стороне клиента

    async def update_drug(self, drug_id: uuid.UUID) -> Optional[Drug]:
        """
        Обновляет все данные о препарате или создаёт новый запрос.

        Returns:
            - pathways: Список путей метаболизма (done)
            - dosage: Словарь дозировок (done)
            - drug_prices: Список цен в разных аптеках (FUTURE: yandex search api)
            - drug_combinations: Полезные и негативные комбинации с другими препаратами (done)
        """
        try:
            drug: Optional[Drug] = await self.repo.get_with_all_relationships(drug_id=drug_id)
            if not drug:
                raise DrugNotFound

            drug = await self.update_dosages(drug=drug)
            drug = await self.update_pathways(drug=drug)
            drug = await self.update_combinations(drug=drug)

            await self.repo.save(drug)
            return drug
        except Exception as ex:
            await self.repo._session.rollback()

            logger.error(f"EXCEPTION: {ex}")
            return None

    async def create_drug(self, drug_name: str):
        """

        :param drug_name: on english
        :return:
        """
        # TODO:
        # 1. check drug_name (бред или нет) -> возврат дв на англ
        # 2. create drug_name + update_drug
        return Drug(
            name=drug_name
        )  # zaglushka

    async def update_dosages(self, drug: Optional[Drug]) -> Optional[Drug]:
        """
        Обновляет три таблицы:
            - Обновляет данные о дозировках препарата.
            - Обновляет синонимы.
            - Обновляет аналоги препарата.
        """

        try:
            assistant_response = assistant.get_dosage(drug_name=drug.name)
            if not assistant_response.drug_name:
                logger.error("ассистент не может найти оффициальное название.")
                raise AssistantResponseError("Couldn't get official drugName from assistant.")
        except Exception as ex:
            raise ex

        try:
            drug.name = assistant_response.drug_name
            drug.latin_name = assistant_response.latin_name
            drug.description = assistant_response.description
            drug.classification = assistant_response.classification
            drug.dosages_fun_fact = assistant_response.dosages_fun_fact
            drug.dosages_sources = assistant_response.sources

            drug.dosages.absorption = assistant_response.pharmacokinetics.absorption
            drug.dosages.metabolism = assistant_response.pharmacokinetics.metabolism
            drug.dosages.excretion = assistant_response.pharmacokinetics.excretion
            drug.dosages.time_to_peak = assistant_response.pharmacokinetics.time_to_peak
        except Exception as ex:
            raise AssistantResponseError(ex)

        # новый временный массив
        dosages_data = []
        for route, methods in assistant_response.dosages.items():
            if methods:
                for method, params in methods.items():
                    if params:
                        dosage = DrugDosage(
                            drug_id=drug.id,
                            route=route,
                            method=method,
                            **params.dict(exclude_none=True)
                        )
                        dosages_data.append(dosage)

        # Обновляем список дозировок
        drug.dosages = dosages_data

        # Обновление остальных списков
        drug.synonyms = [DrugSynonym(synonym=synonym) for synonym in assistant_response.drug_name_ru]
        drug.analogs = [
            DrugAnalog(analog_name=analog.analog_name, percent=analog.percent, difference=analog.difference)
            for analog in assistant_response.analogs
        ]

        drug.updated_at = datetime.now()

        return drug

    async def update_pathways(self, drug: Drug) -> Optional[Drug]:
        """Обновляет пути активации препарата на основе данных от ассистента"""

        try:
            # Получаем данные от ассистента
            assistant_response = assistant.get_pathways(drug.name)
            if not assistant_response:
                raise AssistantResponseError()

            # Обновление Drug модели
            if assistant_response.mechanism_summary:
                drug.pathways_sources = assistant_response.mechanism_summary.sources
                drug.primary_action = assistant_response.mechanism_summary.primary_action
                drug.secondary_actions = assistant_response.mechanism_summary.secondary_actions
                drug.clinical_effects = assistant_response.mechanism_summary.clinical_effects
            else:
                logger.warning("ASSISTANT RESPONSE: Missing mechanism summary!")
                raise AssistantResponseError

            # Создаем новые DrugPathways объекты
            new_pathways = []
            for pathway_data in assistant_response.pathways:
                new_pathways.append(DrugPathway(
                    drug_id=drug.id,
                    receptor=pathway_data.receptor,
                    binding_affinity=pathway_data.binding_affinity,
                    affinity_description=pathway_data.affinity_description,
                    activation_type=pathway_data.activation_type,
                    pathway=pathway_data.pathway,
                    effect=pathway_data.effect,
                    note=pathway_data.note,
                    source=pathway_data.source
                ))

            drug.pathways = new_pathways
            return drug

        except Exception as ex:
            logger.error(f"Failed to update pathways for {drug.name}: {str(ex)}")
            raise ex

    async def update_combinations(self, drug: Drug) -> Optional[Drug]:
        """Update combinations relationship"""

        try:
            assistant_response: AssistantResponseCombinations = assistant.get_combinations(drug_name=drug.name)
            if not assistant_response:
                raise AssistantResponseError()

            new_combinations = []
            for combination in assistant_response.combinations:
                new_combinations.append(DrugCombination(
                    drug_id=drug.id,
                    combination_type=combination.combination_type,
                    substance=combination.substance,
                    effect=combination.effect,
                    risks=combination.risks,
                    products=combination.products,
                    sources=combination.sources
                ))

            drug.combinations = new_combinations
            return drug

        except Exception as ex:
            logger.error(f"Failed to update combinations for {drug_id}: {str(ex)}")
            raise ex
