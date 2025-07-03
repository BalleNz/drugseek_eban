import uuid
from typing import Optional

from sqlalchemy import String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from database.models.base import TimestampsMixin, IDMixin


class Drug(IDMixin, TimestampsMixin):
    __tablename__ = "drugs"
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    # TODO:
    dosages: Mapped[...] = ...
    pathways: Mapped[...] = ...
    combinations: Mapped[...] = ...
    pharmacy_places: Mapped[...] = ...  #


class DrugPrice(IDMixin, TimestampsMixin):
    __tablename__ = "drugs_prices"

    drug_brandname: Mapped[str] = mapped_column(String(100), unique=True)
    price: Mapped[float] = mapped_column(Float)
    shop_url: Mapped[str] = mapped_column(String(100))


class DrugDosages(IDMixin, TimestampsMixin):
    __tablename__ = 'drug_dosages'

    id: Mapped[int] = mapped_column(primary_key=True)
    drug_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('drugs.id'))
    route: Mapped[str] = mapped_column(String(20))  # peroral/parental/etc
    method: Mapped[Optional[str]]  # Для уточнения (intravenous/intramuscular)
    per_time: Mapped[Optional[str]]
    max_day: Mapped[Optional[str]]
    notes: Mapped[Optional[str]]
