import logging
import uuid
from typing import Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.database.models.drug import Drug
from core.database.repository.base import BaseRepository

logger = logging.getLogger("bot.core.repository.drug")


class DrugRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Drug, session=session)

    async def get_with_dosages(self, drug_id: uuid.UUID) -> Optional[Drug]:
        return await self._session.get(
            Drug,
            drug_id,
            options=[selectinload(Drug.dosages)]
        )

    async def save(self, drug: Drug) -> None:
        self._session.add(drug)
        await self._session.commit()
        await self._session.refresh(drug)
