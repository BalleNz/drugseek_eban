import logging
import uuid
from typing import Optional

from sqlalchemy import select, text, exists, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, aliased

from core.database.models.drug import Drug, DrugSynonym
from core.database.repository.base import BaseRepository

logger = logging.getLogger("bot.core.repository.drug")


class DrugRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Drug, session=session)

    async def get_drug_by_user_query(self, user_query: str) -> Optional[Drug]:

        # TODO: pg_trgm

        drug_id: uuid.UUID = await self._session.get(DrugSynonym.where(func.lower(DrugSynonym.synonym) == user_query.lower()))

        result = await self._session.execute(stmt)
        drug: Drug = result.scalar_one_or_none()
        return drug

    async def new_drug(self,) -> Drug:
        ...

    async def get_with_all_relationships(self, drug_id: uuid.UUID) -> Optional[Drug]:
        """Returns Drug with all relation tables"""

        stmt = (
            select(Drug).where(
                Drug.id == drug_id
            )
            .options(selectinload(Drug.pathways, Drug.combinations, Drug.dosages))
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

    async def save(self, drug: Drug) -> None:
        self._session.add(drug)
        await self._session.commit()
        await self._session.refresh(drug)
