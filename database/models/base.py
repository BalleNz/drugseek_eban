from datetime import datetime

from sqlalchemy import UUID, func, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

"""
These classes needs to define mixins for sqlalchemy models.
All generations transits on postgres side.
"""


class TimestampsMixin(DeclarativeBase):
    """
    TIMESTAMPS COLUMNS
    """
    __abstract__ = True

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class IDMixin(DeclarativeBase):
    __abstract__ = True

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=func.gen_random_uuid())
