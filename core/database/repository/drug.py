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
        """
        Using pg_trgm
        """

        fuzzy_stmt = text(
            "SELECT "
            "ds.drug"
            "FROM "
            "drug_synonyms AS ds "
            "WHERE "
            "similarity(lower(ds.synonym), lower(:search_term)) > 0.1 "
            "ORDER BY "
            "score DESC;"
        )
        result = await self._session.execute(fuzzy_stmt, {"search_term": user_query})
        drug: Drug = result.scalar_one_or_none()[0]
        return drug

    # примерный код. TODO: заменить на верхний
    async def get_drug_by_user_query_test(self, user_query: str, allowed_drug_ids: list[uuid.UUID]) -> Optional[Drug]:
        """
        Returns Drug if exists in drug table and allowed on user account.

        :param user_query: запрос пользователя
        :param allowed_drug_ids: drug_ids from user.allowed_drugs
        :return: Drug | None
        """
        stmt = text("""
                SELECT ds.drug_id
                FROM drug_synonyms AS ds
                WHERE 
                    similarity(lower(ds.synonym), lower(:search_term)) > 0.1
                    AND EXISTS (
                        SELECT 1 
                        FROM unnest(:allowed_drug_ids) AS allowed(id)
                        WHERE allowed.id = ds.drug_id
                    )
                ORDER BY similarity(lower(ds.synonym), lower(:search_term)) DESC
                LIMIT 1;
            """)
        result = await self._session.execute(stmt, {"search_term": user_query, "allowed_drug_ids": allowed_drug_ids})
        drug_id = result.scalar_one_or_none()
        return await self.get(drug_id) if drug_id else None

    async def new_drug(self,) -> Drug:
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
