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
    name_ru: Mapped[str] = mapped_column(String(100), unique=True, index=True)
    description: Mapped[str] = mapped_column(TEXT)
    classification: Mapped[str] = mapped_column(String(100))
    analogs: Mapped[Optional[str]] = mapped_column(TEXT)

    # dosages info
    dosages_fun_fact: Mapped[str] = mapped_column(TEXT)
    absorption: Mapped[Optional[str]] = mapped_column(String(100))
    metabolism: Mapped[Optional[str]] = mapped_column(TEXT)
    excretion: Mapped[Optional[str]] = mapped_column(TEXT)
    time_to_peak: Mapped[Optional[str]] = mapped_column(String(100))

    combinations: Mapped[...] = ...
    drug_prices: Mapped[...] = ...  #

    # pathways generation
    primary_action: Mapped[Optional[str]] = mapped_column(String(100))
    secondary_actions: Mapped[Optional[str]] = mapped_column(String(100)) # TODO
    clinical_effects: Mapped[Optional[str]] = mapped_column(TEXT)

    pathways_sources: Mapped[Optional[str]] = mapped_column(TEXT)
    dosages_sources: Mapped[str] = mapped_column(TEXT)

    # Отношение к DrugDosage
    dosages: Mapped[list["DrugDosages"]] = relationship(
        back_populates="drug",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    pathways: Mapped[list["DrugPathways"]] = relationship(
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


class DrugPathways(IDMixin):
    __tablename__ = "drug_pathways"

    drug_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey('drugs.id', ondelete='CASCADE'),
        nullable=False
    )
    drug: Mapped["Drug"] = relationship(back_populates="pathways")

    # Основные поля для хранения данных о путях активации
    receptor: Mapped[str] = mapped_column(String(100), nullable=False)  # Название рецептора (например, "α2A-адренорецептор")
    binding_affinity: Mapped[Optional[str]] = mapped_column(String(50))  # Ki/IC50/EC50 (например, "Ki = 2.1 нМ")
    affinity_description: Mapped[Optional[str]] = mapped_column(String(100))  # Описание силы связывания (например, "очень сильное связывание")
    activation_type: Mapped[str] = mapped_column(String(50), nullable=False)  # Тип активации (например, "antagonist")
    pathway: Mapped[Optional[str]] = mapped_column(String(100))  # Сигнальный путь (например, "Gi/o protein cascade")
    effect: Mapped[Optional[str]] = mapped_column(String(100))  # Физиологический эффект (например, "повышение норадреналина")

    # Дополнительные технические поля
    source: Mapped[Optional[str]] = mapped_column(String(100))  # Источник данных (например, "DrugBank")
    note: Mapped[Optional[str]] = mapped_column(TEXT)  # Дополнительные примечания

    __table_args__ = (
        UniqueConstraint('drug_id', 'receptor', 'activation_type', name='uq_drug_pathway'),
    )


class DrugPrice(IDMixin, TimestampsMixin):
    __tablename__ = "drug_prices"

    drug_brandname: Mapped[str] = mapped_column(String(100), unique=True)
    price: Mapped[float] = mapped_column(Float)
    shop_url: Mapped[str] = mapped_column(String(100))


class DrugDosages(IDMixin):
    __tablename__ = 'drug_dosages'

    drug_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey('drugs.id', ondelete='CASCADE'),
        nullable=False
    )
    drug: Mapped["Drug"] = relationship(back_populates="dosages")

    route: Mapped[Optional[str]] = mapped_column(String(30))  # peroral / parental / ...
    method: Mapped[Optional[str]] = mapped_column(String(30))  # intravenous / intramuscular

    per_time: Mapped[Optional[str]] = mapped_column(String(100))
    max_day: Mapped[Optional[str]] = mapped_column(String(100))

    # for peroral and intramuscular only
    per_time_weight_based: Mapped[Optional[str]] = mapped_column(String(100))
    max_day_weight_based: Mapped[Optional[str]] = mapped_column(String(100))

    onset: Mapped[Optional[str]] = mapped_column(String(100))
    half_life: Mapped[Optional[str]] = mapped_column(String(100))
    elimination: Mapped[Optional[str]] = mapped_column(TEXT)
    duration: Mapped[Optional[str]] = mapped_column(String(100))

    notes: Mapped[Optional[str]] = mapped_column(String(100))

    __table_args__ = (
        UniqueConstraint('drug_id', 'route', 'method', name='uq_drug_dosage'),
    )
