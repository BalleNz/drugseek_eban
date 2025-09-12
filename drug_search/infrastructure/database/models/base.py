from abc import abstractmethod
from datetime import datetime
from typing import Type, Any, TypeVar, Optional, Union

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

        relationships = [rel.key for rel in cls.__mapper__.relationships]

        rel_data: dict = dict()
        for rel in relationships:
            if rel in model_data:
                rel_data[rel] = model_data.pop(rel)

        model: M = cls(**model_data, **kwargs)

        for rel_name, rel_items in rel_data.items():
            if rel_items is not None:
                # Получаем класс связанной модели из отношения
                rel_property = getattr(cls, rel_name).property
                rel_class = rel_property.mapper.class_

                # Создаем объекты связанных моделей
                related_objects = []
                for item_data in rel_items:
                    if isinstance(item_data, dict):
                        # Если это словарь, создаем объект модели
                        related_objects.append(rel_class(**item_data))
                    else:
                        # Если это Pydantic модель, конвертируем в SQLAlchemy
                        related_objects.append(rel_class.from_pydantic(item_data))
                setattr(model, rel_name, related_objects)
        return model

    def get_schema(self) -> Union[S, list[None]]:
        model_data = {}
        schema_fields = self.schema_class.model_fields.keys()

        for column in self.__table__.columns:
            # проверка, есть ли такой столбец в схеме
            if column.name in schema_fields:
                model_data[column.name] = getattr(self, column.name)
        if model_data:
            return self.schema_class.model_validate(model_data)
        return []
