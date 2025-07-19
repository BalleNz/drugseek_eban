import logging
import uuid
from typing import Optional

from fastapi import Depends
from sqlalchemy import select, text, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.database.models.drug import Drug, DrugSynonym
from core.database.repository.base import BaseRepository
from database.engine import get_async_session

logger = logging.getLogger("bot.core.repository.drug")


class DrugRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Drug, session=session)

    async def find_drug_by_query(self, user_query: str) -> Optional[Drug]:
        """
        Поиск препарата по триграммному сходству с синонимами (один запрос).
        Возвращает Drug с максимальным similarity или None.
        """
        stmt = (
            select(Drug)
            .join(Drug.synonyms)
            .where(
                func.similarity(
                    func.lower(DrugSynonym.synonym),
                    func.lower(user_query)
                ) > 0.1
            )
            .order_by(
                func.similarity(
                    func.lower(DrugSynonym.synonym),
                    func.lower(user_query)
                ).desc()
            )
            .limit(1)
            .options(
                selectinload(Drug.analogs),
                selectinload(Drug.pathways),
                selectinload(Drug.synonyms)
            )
        )

        result = await self._session.execute(stmt)
        return result.scalar_one_or_none()

    async def new_drug(self, ) -> Drug:
        ...

    async def get_with_all_relationships(self, drug_id: uuid.UUID) -> Optional[Drug]:
        """Returns Drug with all relation tables"""

        stmt = (
            select(Drug).where(
                Drug.id == drug_id
            )
            .options(selectinload(Drug.pathways, Drug.combinations, Drug.dosages, DrugSynonym))
        )

        result = await self._session.execute(stmt)
        drug = result.scalars().one_or_none()
        return drug

    async def get_with_pathways(self, drug_id: uuid.UUID) -> Optional[Drug]:
        """Returns Drug with pathways relation table"""

        stmt = (
            select(Drug).where(
                Drug.id == drug_id
            )
            .options(selectinload(Drug.pathways))
        )

        result = await self._session.execute(stmt)
        drug = result.scalars().one_or_none()
        return drug

    async def get_with_combinations(self, drug_id: uuid.UUID) -> Optional[Drug]:
        """Returns Drug with combinations relation table"""

        stmt = (
            select(Drug).where(
                Drug.id == drug_id
            )
            .options(selectinload(Drug.combinations))
        )

        result = await self._session.execute(stmt)
        drug = result.scalars().one_or_none()
        return drug

    async def get_with_dosages(self, drug_id: uuid.UUID) -> Optional[Drug]:
        """Returns Drug with dosages relation table"""

        stmt = (
            select(Drug).where(
                Drug.id == drug_id
            )
            .options(selectinload(Drug.dosages))
        )

        result = await self._session.execute(stmt)
        drug = result.scalars().one_or_none()
        return drug

    async def save(self, drug: Drug) -> Drug:
        self._session.add(drug)
        await self._session.commit()
        await self._session.refresh(drug)

        return drug


def get_drug_repository(session: AsyncSession = Depends(get_async_session)) -> DrugRepository:
    return DrugRepository(session=session)
