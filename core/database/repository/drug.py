import logging
from typing import Optional

from sqlalchemy import select, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.database.models.drug import Drug
from core.database.repository.base import BaseRepository

logger = logging.getLogger("bot.core.repository.drug")


class DrugRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Drug, session=session)

    async def get_with_pathways_by_name(self, drug_name: str) -> Optional[Drug]:
        stmt = (
            select(Drug)
            .where(
                or_(
                    Drug.name_ru == drug_name, Drug.name == drug_name
                )
            )
            .options(selectinload(Drug.pathways))
        )

        result = await self._session.execute(stmt)

        # Извлекаем все результаты
        drug = result.scalars().one_or_none()

        return drug

    async def get_with_dosages_by_name(self, drug_name: str) -> Optional[Drug]:
        stmt = (
            select(Drug)
            .where(
                or_(
                    Drug.name_ru == drug_name, Drug.name == drug_name
                )
            )
            .options(selectinload(Drug.dosages))
        )

        result = await self._session.execute(stmt)

        # Извлекаем все результаты
        drug = result.scalars().one_or_none()

        return drug

    async def save(self, drug: Drug) -> None:
        self._session.add(drug)
        await self._session.commit()
        await self._session.refresh(drug)
