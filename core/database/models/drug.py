import uuid
from typing import Optional

from sqlalchemy import String, Float, ForeignKey, TEXT, UniqueConstraint, ARRAY, Index, func
from sqlalchemy.dialects.postgresql import UUID as PG_UUID  # Важно импортировать UUID для PostgreSQL
from sqlalchemy.orm import Mapped, mapped_column, relationship

from core.database.models.base import TimestampsMixin, IDMixin


class Drug(IDMixin, TimestampsMixin):
    __tablename__ = "drugs"

    name: Mapped[str] = mapped_column(String(100))  # действующее вещество
    latin_name: Mapped[Optional[str]] = mapped_column(String(100))
    description: Mapped[str] = mapped_column(TEXT)
    classification: Mapped[str] = mapped_column(String(100))
    analogs: Mapped[Optional[str]] = mapped_column(TEXT)

    # dosages info
    dosages_fun_fact: Mapped[str] = mapped_column(TEXT)
    absorption: Mapped[Optional[str]] = mapped_column(String(100))
    metabolism: Mapped[Optional[str]] = mapped_column(TEXT)
    excretion: Mapped[Optional[str]] = mapped_column(TEXT)
    time_to_peak: Mapped[Optional[str]] = mapped_column(String(100))

    drug_prices: Mapped[...] = ...  #

    # pathways generation
    primary_action: Mapped[Optional[str]] = mapped_column(String(100))
    secondary_actions: Mapped[Optional[str]] = mapped_column(String(100))  # TODO
    clinical_effects: Mapped[Optional[str]] = mapped_column(TEXT)

    pathways_sources: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String))
    dosages_sources: Mapped[list[str]] = mapped_column(ARRAY(String))

    # Отношение к DrugDosage
    dosages: Mapped[list["DrugDosage"]] = relationship(
        back_populates="drug",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    pathways: Mapped[list["DrugPathway"]] = relationship(
        back_populates="drug",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    combinations: Mapped[list["DrugCombination"]] = relationship(
        back_populates="drug",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    synonyms: Mapped[list["DrugSynonym"]] = relationship(
        back_populates="drug",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    __table_args__ = (
        Index(
            'trgm_drug_name_idx',
            func.lower(name),  # Используем func.lower для индексации нижнего регистра
            postgresql_using='gin',  # Указываем тип индекса GIN
            postgresql_ops={func.lower(name): 'gin_trgm_ops'}  # Указываем операторный класс
        ),
        UniqueConstraint("drug_id", "name"),
        Index("idx_drugs_name_lower", func.lower(name), postgresql_using="btree")
    )


class DrugSynonym(IDMixin):
    __tablename__ = "drug_synonyms"

    drug_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("drugs.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    synonym: Mapped[str] = mapped_column(
        String(100, collation="ru_RU.utf8"),
        unique=True,
        comment="одно из названий препарата на русском"
    )

    __table_args__ = (
        UniqueConstraint("drug_id", "synonym", name="uq_drug_synonym"),

        # B-tree индекс для точного совпадения
        Index("idx_drug_synonyms_lower", func.lower(synonym), postgresql_using="btree"),

        # GIN индекс для нечеткого поиска (триграммы) регистронезависимого поиска
        Index(
            'trgm_drug_synonyms_lower_idx',
            func.lower(synonym),
            postgresql_using='gin',
            postgresql_ops={func.lower(synonym): 'gin_trgm_ops'}
        )
    )


class DrugCombination(IDMixin):
    __tablename__ = "drug_combinations"

    drug_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("drugs.id", ondelete="CASCADE"),
        nullable=False
    )
    drug: Mapped["Drug"] = relationship(back_populates="combinations")

    combination_type: Mapped[str] = mapped_column(String(10))  # 'good' или 'bad'
    substance: Mapped[str] = mapped_column(String(100))  # ДВ / ДВ или Класс для плохих комбинаций
    effect: Mapped[str] = mapped_column(TEXT)
    risks: Mapped[Optional[str]] = mapped_column(TEXT)  # Только для bad
    products: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String))  # название препаратов с этим ДВ
    sources: Mapped[list[str]] = mapped_column(ARRAY(String))


class DrugPathway(IDMixin):
    __tablename__ = "drug_pathways"

    drug_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey('drugs.id', ondelete='CASCADE'),
        nullable=False
    )
    drug: Mapped["Drug"] = relationship(back_populates="pathways")

    # Основные поля для хранения данных о путях активации
    receptor: Mapped[str] = mapped_column(String(100),
                                          nullable=False)  # Название рецептора (например, "α2A-адренорецептор")
    binding_affinity: Mapped[Optional[str]] = mapped_column(String(50))  # Ki/IC50/EC50 (например, "Ki = 2.1 нМ")
    affinity_description: Mapped[Optional[str]] = mapped_column(
        String(100))  # Описание силы связывания (например, "очень сильное связывание")
    activation_type: Mapped[str] = mapped_column(String(50), nullable=False)  # Тип активации (например, "antagonist")
    pathway: Mapped[Optional[str]] = mapped_column(String(100))  # Сигнальный путь (например, "Gi/o protein cascade")
    effect: Mapped[Optional[str]] = mapped_column(
        String(100))  # Физиологический эффект (например, "повышение норадреналина")

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


class DrugDosage(IDMixin):
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
