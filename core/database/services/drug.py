from sqlalchemy.ext.asyncio import AsyncSession

from core.database.repository.drug import DrugRepository


class DrugService:
    def __init__(self, repo: DrugRepository):
        self._repo = repo

    async def update_drug(self, drug) -> bool:
        """
        Обновляет данные о препарате или создаёт новый запрос.

        Returns:
            - pathways: Список путей метаболизма
            - price: Текущая цена в USD
            - dosage: Словарь дозировок
            - drug_prices: Список цен в разных аптеках
            - fun_fact: Интересный факт о препарате с нотками чёрного юмора
        """
        return await self._repo.drug_update()

