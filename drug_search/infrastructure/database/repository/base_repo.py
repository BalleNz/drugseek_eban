from typing import TypeVar, Generic, Type, Optional, Sequence
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import update, delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from drug_search.infrastructure.database.models.base import IDMixin

M = TypeVar("M", bound=IDMixin)
S = TypeVar("S", bound=BaseModel)


class BaseRepository(Generic[M]):
    def __init__(self, model: Type[M], session: AsyncSession):
        self.model = model
        self.session = session

    async def save(self, model: M) -> S:
        """Saves all changes and refresh model."""
        self.session.add(model)
        await self.session.commit()
        await self.session.refresh(model)
        return model.get_schema()

    async def save_from_schema(self, schema: S) -> S:
        """Saves all changes and refresh model."""
        model: M = self.model.from_pydantic(schema)
        return await self.save(model)

    async def get(self, id: UUID) -> Optional[S]:
        """Get schema by primary key ID."""
        model: M = await self.session.get(self.model, id)
        return model.get_schema()

    async def get_model(self, id: UUID) -> Optional[M]:
        """Get model by primary key ID."""
        model: M = await self.session.get(self.model, id)
        return model

    async def get_all(self) -> Sequence[S]:
        """Returns all models"""
        result = await self.session.execute(select(self.model))
        models = result.scalars().all()
        return [model.get_schema() for model in models]

    async def create(self, model: M) -> S:
        """Create new model by instance."""
        try:
            self.session.add(model)
            await self.session.commit()
            await self.session.refresh(model)  # refresh from db (generated ID for example)
            return model.get_schema()
        except:
            await self.session.rollback()
            raise

    async def update(self, id: UUID, **values) -> Optional[S]:
        """
        Refresh model if exist on DB, or returns None.
        """
        stmt = (
            update(self.model)
            .where(self.model.id == id)
            .values(**values)
            .returning(self.model)
        )
        result = await self.session.execute(stmt)
        await self.session.commit()
        model: M = result.scalar_one_or_none()
        if model:
            return model.get_schema()
        return None

    async def delete(self, id: UUID) -> bool:
        """Delete model by ID. Returns True if deleted, False if not found."""
        result = await self.session.execute(
            delete(self.model).where(self.model.id == id)
        )
        await self.session.commit()
        return result.rowcount > 0
