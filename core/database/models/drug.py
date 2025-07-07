import uuid
from dataclasses import dataclass
from typing import Optional

from sqlalchemy import String, Float, ForeignKey, TEXT, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID as PG_UUID  # Важно импортировать UUID для PostgreSQL
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.models.base import TimestampsMixin, IDMixin


@dataclass
class DosageView:
    route: str
    method: Optional[str]
    per_time: Optional[str]
    max_day: Optional[str]
    per_time_weight_based: Optional[str]
    max_day_weight_based: Optional[str]
    notes: Optional[str]


class Drug(IDMixin, TimestampsMixin):
    __tablename__ = "drugs"
    name: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[str] = mapped_column(TEXT)
    classification: Mapped[str] = mapped_column(String(100))

    pathways: Mapped[...] = ...
    combinations: Mapped[...] = ...
    drug_prices: Mapped[...] = ...  #

    dosages_fun_fact: Mapped[str] = mapped_column(String(100))

    # Отношение к DrugDosage
    dosages: Mapped[list["DrugDosages"]] = relationship(
        back_populates="drug",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    @hybrid_property
    def dosages_view(self) -> dict[str, dict[str, DosageView]]:
        """Группирует дозировки по route и method в удобную структуру"""
        result = {}
        for dosage in self.dosages:
            if dosage.route not in result:
                result[dosage.route] = {}

            result[dosage.route][dosage.method] = DosageView(
                route=dosage.route,
                method=dosage.method,
                per_time=dosage.per_time,
                max_day=dosage.max_day,
                per_time_weight_based=dosage.per_time_weight_based,
                max_day_weight_based=dosage.max_day_weight_based,
                notes=dosage.notes
            )
        return result


class DrugPrice(IDMixin, TimestampsMixin):
    __tablename__ = "drug_prices"

    drug_brandname: Mapped[str] = mapped_column(String(100), unique=True)
    price: Mapped[float] = mapped_column(Float)
    shop_url: Mapped[str] = mapped_column(String(100))


class DrugDosages(IDMixin, TimestampsMixin):
    __tablename__ = 'drug_dosages'

    id: Mapped[int] = mapped_column(primary_key=True)

    drug_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey('drugs.id', ondelete='CASCADE'),
        nullable=False
    )
    drug: Mapped["Drug"] = relationship(back_populates="dosages")

    route: Mapped[str] = mapped_column(String(20))  # peroral / parental / ...
    method: Mapped[Optional[str]]  # intravenous / intramuscular

    per_time: Mapped[Optional[str]] = mapped_column(String(100))
    max_day: Mapped[Optional[str]] = mapped_column(String(100))

    # for peroral and intramuscular only
    per_time_weight_based: Mapped[Optional[str]] = mapped_column(String(100))
    max_day_weight_based: Mapped[Optional[str]] = mapped_column(String(100))

    notes: Mapped[Optional[str]] = mapped_column(String(100))

    __table_args__ = (
        UniqueConstraint('drug_id', 'route', 'method', name='uq_drug_dosage'),
    )
