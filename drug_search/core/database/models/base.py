from datetime import datetime

from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy import func, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

"""
These classes needs to define mixins for sqlalchemy models.
All generations transits on postgres side.
"""


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
