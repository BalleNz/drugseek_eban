from typing import TypeVar, Generic, Type, Optional
from uuid import UUID

from sqlalchemy import update, delete
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from drug_search.core.database.models.base import IDMixin

T = TypeVar("T", bound=IDMixin)


class BaseRepository(Generic[T]):
    def __init__(self, model: Type[T], session: AsyncSession):
        self._model = model  # table model
        self._session = session

    async def save(self, model: T) -> T:
        """Saves all changes and refresh model."""
        self._session.add(model)
        await self._session.commit()
        await self._session.refresh(model)

        return model

    async def get(self, id: UUID) -> Optional[T]:
        """Get model by primary key ID."""
        return await self._session.get(self._model, id)

    async def create(self, model: T) -> T:
        """Create new model by instance."""
        try:
            self._session.add(model)
            await self._session.commit()
            await self._session.refresh(model)  # refresh from db (generated ID for example)
            return model
        except SQLAlchemyError:
            await self._session.rollback()
            raise

    async def update(self, id: UUID, **values) -> Optional[T]:
        """
        Refresh model if exist on DB, or returns None.
        """
        stmt = (
            update(self._model)
            .where(self._model.id == id)
            .values(**values)
            .returning(self._model)
        )
        result = await self._session.execute(stmt)
        await self._session.commit()
        return result.scalar_one_or_none()

    async def delete(self, id: UUID) -> bool:
        """Delete model by ID. Returns True if deleted, False if not found."""
        result = await self._session.execute(
            delete(self._model).where(self._model.id == id)
        )
        await self._session.commit()
        return result.rowcount > 0
