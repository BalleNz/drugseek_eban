import logging
import uuid
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import ValidationError

from core.database.models.drug import Drug, DrugDosages
from core.database.repository.drug import DrugRepository
from core.schemas.drug import AssistantDosageResponse
from neuro_assistant.assistant import assistant


class DrugService:
    def __init__(self, repo: DrugRepository):
        self.repo = repo

    async def update_drug(self, drug_name: str) -> Optional[bool]:
        """
        Обновляет данные о препарате или создаёт новый запрос.

        Returns:
            - drug_description: Описание препарата
            - pathways: Список путей метаболизма
            - dosage: Словарь дозировок (done)
            - drug_prices: Список цен в разных аптеках
            - drug_combinations: Полезные и негативные комбинации с другими препаратами
        """
        await self.update_drug_dosages(drug_name)
        ...

    async def update_drug_dosages(self, drug_name: str) -> Optional[Drug]:
        """Обновляет данные о дозировках препарата."""
        # Получаем и валидируем данные от ассистента
        assistant_response = assistant.get_dosage(drug_name)

        # Получаем препарат с дозировками
        drug = await self.repo.get_with_dosages_by_name(drug_name)
        if not drug:
            drug = Drug(
                id=uuid.uuid4(),
                name=assistant_response.drug_name,
                description="",  # Можно добавить запрос описания у ассистента
                classification="",  # Аналогично
                dosages_fun_fact=assistant_response.dosages_fun_fact,
                created_at=datetime.now(),
                updated_at=datetime.now()
            )

        # Обновляем dosages_fun_fact
        if assistant_response.dosages_fun_fact:
            drug.dosages_fun_fact = assistant_response.dosages_fun_fact
        else:
            logging.warning("ASSISTANT RESPONSE HAS NOT DOSAGES FUN FACT")

        if assistant_response.description:
            drug.description = assistant_response.description
        else:
            logging.warning("ASSISTANT RESPONSE HAS NOT DOSAGES FUN FACT")

        if assistant_response.classification:
            drug.classification = assistant_response.classification
        else:
            logging.warning("ASSISTANT RESPONSE HAS NOT DOSAGES FUN FACT")

        # Обновляем дозировки
        if assistant_response.dosages:
            self._update_drug_dosages(drug, assistant_response.dosages)
        else:
            logging.error("ASSISTANT RESPONSE IS NONE")

        # Сохраняем изменения
        await self.repo.save(drug)
        return drug

    def _update_drug_dosages(self, drug: Drug, new_dosages_data: dict) -> None:
        """Основная логика обновления дозировок"""
        # Создаем словарь существующих дозировок
        existing_map = {(d.route, d.method): d for d in drug.dosages}

        # Обрабатываем новые дозировки
        updated_dosages = []
        for route, methods in new_dosages_data.items():
            for method, params in methods.items():
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
