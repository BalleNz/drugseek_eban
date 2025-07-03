import uuid
from typing import Optional

from sqlalchemy import String, Float, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column

from core.database.models.base import TimestampsMixin, IDMixin


class Drug(IDMixin, TimestampsMixin):
    __tablename__ = "drugs"
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)

    # TODO:
    dosages: Mapped[...] = ...
    pathways: Mapped[...] = ...
    combinations: Mapped[...] = ...
    drug_prices: Mapped[...] = ...  #
    fun_fact: Mapped[str] = mapped_column(String(100))


class DrugPrice(IDMixin, TimestampsMixin):
    __tablename__ = "drug_prices"

    drug_brandname: Mapped[str] = mapped_column(String(100), unique=True)
    price: Mapped[float] = mapped_column(Float)
    shop_url: Mapped[str] = mapped_column(String(100))


class DrugDosages(IDMixin, TimestampsMixin):
    __tablename__ = 'drug_dosages'

    id: Mapped[int] = mapped_column(primary_key=True)
    drug_id: Mapped[uuid.UUID] = mapped_column(ForeignKey('drugs.id'))

    route: Mapped[str] = mapped_column(String(20))  # peroral / parental / ...
    method: Mapped[Optional[str]]  # intravenous / intramuscular

    per_time: Mapped[Optional[str]]
    max_day: Mapped[Optional[str]]

    # for peroral and intramuscular only
    per_time_weight_based: Mapped[Optional[str]]
    max_day_weight_based: Mapped[Optional[str]]

    notes: Mapped[Optional[str]]
