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

    async def update_drug(self, drug) -> Optional[bool]:
        """
        Обновляет данные о препарате или создаёт новый запрос.

        Returns:
            - pathways: Список путей метаболизма
            - price: Текущая цена в USD
            - dosage: Словарь дозировок
            - drug_prices: Список цен в разных аптеках
            - fun_fact: Интересный факт о препарате с нотками чёрного юмора
        """
        await self.update_drug_dosages(drug.id)
        ...

    async def update_drug_dosages(self, drug_id: UUID) -> Optional[Drug]:
        # Получаем препарат с дозировками
        drug = await self.repo.get_with_dosages(drug_id)
        if not drug:
            return None

        # Получаем и валидируем данные от ассистента
        raw_data = assistant.get_dosage(drug.name)
        try:
            update_data = AssistantDosageResponse(**raw_data)
        except ValidationError as e:
            raise ValueError(f"Invalid assistant response: {e}")

        # Обновляем fun_fact
        if update_data.fun_fact:
            drug.fun_fact = update_data.fun_fact

        # Обновляем дозировки
        if update_data.dosages:
            self._update_drug_dosages(drug, update_data.dosages)

        # Сохраняем изменения
        await self.repo.save(drug)
        return drug

    def _update_drug_dosages(self, drug: Drug, new_dosages_data: dict):
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
