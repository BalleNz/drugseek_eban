from abc import abstractmethod
from datetime import datetime
from typing import Type, Any, TypeVar

from pydantic import BaseModel
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import func, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

"""
These classes needs to define mixins for sqlalchemy models.
All generations transits on postgres side.
"""

M = TypeVar("M", bound='IDMixin')
S = TypeVar("S", bound=BaseModel)


class TimestampsMixin:
    """
    Mixin for adding timestamp fields to ORM models.

    This mixin provides standard `created_at` and `updated_at` columns for
    automatically tracking the creation and last update times of database records.
    """

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class IDMixin(DeclarativeBase):
    """
    Mixin for adding ID field to ORM models.
    """
    __abstract__ = True

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=func.gen_random_uuid())

    @property
    @abstractmethod
    def schema_class(cls) -> Type[S]:
        raise NotImplementedError

    @classmethod
    def from_pydantic(cls: Type[M], schema: S, **kwargs: Any) -> M:
        """Создает SQLAlchemy модель из схемы Pydantic"""
        model_data: dict = schema.model_dump(exclude_unset=True)
        return cls(**model_data, **kwargs)

    def get_schema(self) -> S:
        model_data = {}
        for column in self.__table__.columns:
            model_data[column.name] = getattr(self, column.name)

        # 2. Затем передаём словарь в Pydantic для валидации
        return self.schema_class.model_validate(model_data)
