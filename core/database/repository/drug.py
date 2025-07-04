from sqlalchemy.ext.asyncio import AsyncSession

from core.database.models.drug import Drug
from core.database.repository.base import BaseRepository


class DrugRepository(BaseRepository):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Drug, session=session)

    async def drug_update(self):
        ...

