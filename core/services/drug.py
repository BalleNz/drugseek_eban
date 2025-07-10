import logging
import uuid
from typing import Optional

from core.database.models.drug import Drug, DrugDosages, DrugPathways, DrugCombinations
from core.database.repository.drug import DrugRepository
from core.exceptions import DrugNotFound
from exceptions import AssistantResponseError
from neuro_assistant.assistant import assistant
from schemas.drug import AssistantResponseCombinations

logger = logging.getLogger("bot.core.drug_service")


class DrugService:
    def __init__(self, repo: DrugRepository):
        self.repo = repo

    async def new_drug(self, drug_name: str) -> Optional[bool]:
        """
        Обновляет все данные о препарате или создаёт новый запрос.

        Returns:
            - pathways: Список путей метаболизма (done)
            - dosage: Словарь дозировок (done)
            - drug_prices: Список цен в разных аптеках
            - drug_combinations: Полезные и негативные комбинации с другими препаратами (...)
        """
        await self.update_drug_dosages_description(drug_name)
        ...

    async def update_drug_dosages_description(self, drug_name: str) -> Optional[Drug]:
        """
        Первый запрос.
        Обновляет данные о дозировках препарата.
        """
        # Получаем и валидируем данные от ассистента
        try:
            assistant_response = assistant.get_dosage(drug_name)
            if not assistant_response.drug_name:
                logger.error("Введено неправильно название препарата, ассистент не может найти оффициальное название.")
                raise AssistantResponseError("Wrong input drug / Couldn't get official drugName from assistant.")
        except Exception as ex:
            raise ex

        # Получаем препарат с дозировками
        # подразумевается что пользователь ввел на русском или англ

        # TODO: сделать отдельный промпт  чтобы правильно интерпретировал ввод пользователя + защита от бреда пользователя + ограничение на размер сообщения

        drug = await self.repo.get_with_dosages_by_name(drug_name)

        if not drug:
            # ЗДЕСЬ СОЗДАЕТСЯ НОВЫЙ ЭКЗЕМПЛЯР DRUG
            drug = Drug(
                id=uuid.uuid4(),
                name=assistant_response.drug_name,
                name_ru=assistant_response.drug_name_ru,
                description=assistant_response.description,
                classification=assistant_response.classification,
                dosages_fun_fact=assistant_response.dosages_fun_fact,
                dosages_sources=assistant_response.sources,
                absorption=assistant_response.pharmacokinetics.absorption,
                metabolism=assistant_response.pharmacokinetics.metabolism,
                excretion=assistant_response.pharmacokinetics.excretion,
                time_to_peak=assistant_response.pharmacokinetics.time_to_peak,
                analogs=assistant_response.analogs
                # created_at=datetime.now(),  # ? on server side
                # updated_at=datetime.now(),
            )

        # новый временный массив
        dosages_data = []
        for route, methods in assistant_response.dosages.items():
            if methods:
                for method, params in methods.items():
                    if params:
                        dosage = DrugDosages(
                            drug_id=drug.id,
                            route=route,
                            method=method,
                            **params.dict(exclude_none=True)
                        )
                        dosages_data.append(dosage)

        # Обновляем список дозировок
        drug.dosages = dosages_data

        # Сохраняем изменения
        await self.repo.save(drug)
        return drug

    async def update_pathways(self, drug_name: str) -> Optional[Drug]:
        """Обновляет пути активации препарата на основе данных от ассистента"""
        # Получаем препарат с существующими путями активации
        drug = await self.repo.get_with_pathways_by_name(drug_name)
        if not drug:
            raise DrugNotFound()

        try:
            # Получаем данные от ассистента
            assistant_response = assistant.get_pathways(drug.name_ru)
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

            # Создаем новые DrugPathways объекты
            new_pathways = []
            for pathway_data in assistant_response.pathways:
                new_pathways.append(DrugPathways(
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

            await self.repo.save(drug)
            return drug

        except Exception as ex:
            logger.error(f"Failed to update pathways for {drug_name}: {str(ex)}")
            raise ex

    async def update_combinations(self, drug_name: str) -> Optional[Drug]:
        drug: Drug = await self.repo.get_with_combinations_by_name(drug_name=drug_name)
        if not drug:
            raise DrugNotFound()

        try:
            assistant_response: AssistantResponseCombinations = assistant.get_combinations(drug_name=drug_name)
            if not assistant_response:
                raise AssistantResponseError()

            new_combinations = []
            for combination in assistant_response.combinations:
                new_combinations.append(DrugCombinations(
                    drug_id=drug.id,
                    combination_type=combination.combination_type,
                    substance=combination.substance,
                    effect=combination.effect,
                    risks=combination.risks,
                    products=combination.products,
                    sources=combination.sources
                ))

            drug.combinations = new_combinations

            await self.repo.save(drug)
            return drug

        except Exception as ex:
            logger.error(f"Failed to update combinations for {drug_name}: {str(ex)}")
            raise ex
