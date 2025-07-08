import logging
import uuid
from datetime import datetime
from typing import Optional

from core.database.models.drug import Drug, DrugDosages, DrugPathways
from core.database.repository.drug import DrugRepository
from core.exceptions import DrugNotFound
from neuro_assistant.assistant import assistant

logger = logging.getLogger("bot.core.drug_service")


class DrugService:
    def __init__(self, repo: DrugRepository):
        self.repo = repo

    async def new_drug(self, drug_name: str) -> Optional[bool]:
        """
        Обновляет все данные о препарате или создаёт новый запрос.

        Returns:
            - drug_description, classification: Описание препарата и классификация
            - pathways: Список путей метаболизма (...)
            - dosage: Словарь дозировок (done)
            - drug_prices: Список цен в разных аптеках
            - drug_combinations: Полезные и негативные комбинации с другими препаратами
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
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

        # Обновляем дозировки
        self._update_drug_dosages_description(drug, assistant_response.dosages)

        # Сохраняем изменения
        await self.repo.save(drug)
        return drug

    def _update_drug_dosages_description(self, drug: Drug, new_dosages_data: dict) -> None:
        """Основная логика обновления дозировок"""
        # Создаем словарь существующих дозировок
        existing_map = {(d.route, d.method): d for d in drug.dosages}

        # Обрабатываем новые дозировки
        updated_dosages = []
        for route, methods in new_dosages_data.items():
            for method, params in methods.items():
                if not params:
                    continue
                key = (route, method)

                # Обновляем существующую или создаем новую
                if key in existing_map:
                    dosage = existing_map[key]
                    for field, value in params.dict(exclude_none=True).items():
                        if hasattr(dosage, field):
                            setattr(dosage, field, value)
                else:
                    dosage = DrugDosages(
                        drug_id=drug.id,
                        route=route,
                        method=method,
                        **params.dict(exclude_none=True)
                    )

                updated_dosages.append(dosage)

        # Обновляем список дозировок
        drug.dosages = updated_dosages

    async def update_pathways(self, drug_name: str) -> Optional[Drug]:
        """Обновляет пути активации препарата на основе данных от ассистента"""
        # Получаем препарат с существующими путями активации
        drug = await self.repo.get_with_pathways_by_name(drug_name)
        if not drug:
            raise DrugNotFound()

        try:
            # Получаем данные от ассистента
            assistant_response = assistant.get_pathways(drug.name_ru)

            # Обновляем источники
            if assistant_response.sources:
                drug.pathways_sources = ", ".join(assistant_response.sources)

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
                    effect=pathway_data.effect
                ))

            # Полная замена существующих путей активации
            drug.pathways = new_pathways

            # Сохраняем изменения
            await self.repo.save(drug)
            return drug

        except Exception as ex:
            logger.error(f"Failed to update pathways for {drug_name}: {str(ex)}")
            raise ex
