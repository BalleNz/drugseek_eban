import uuid
from datetime import date
from typing import Optional, Type, TypeVar

from pydantic import BaseModel
from sqlalchemy import String, Float, ForeignKey, Text, UniqueConstraint, ARRAY, Index, func, Date, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID  # Важно импортировать UUID для PostgreSQL
from sqlalchemy.orm import Mapped, mapped_column, relationship

from drug_search.infrastructure.database.models.base import TimestampsMixin, IDMixin
from drug_search.core.schemas import DrugAnalogResponse, DrugCombinationResponse, DrugPathwayResponse, \
    DrugResearchResponse, DrugSynonymResponse, DrugDosageResponse, DrugSchema

M = TypeVar("M", bound=IDMixin)
S = TypeVar("S", bound=BaseModel)


class Drug(IDMixin, TimestampsMixin):
    __tablename__ = "drugs"

    name: Mapped[str] = mapped_column(String(100), unique=True)  # ДВ на англ
    name_ru: Mapped[Optional[str]] = mapped_column(String(100))  # ДВ на русском
    latin_name: Mapped[Optional[str]] = mapped_column(String(100))
    description: Mapped[Optional[str]] = mapped_column(Text)
    classification: Mapped[Optional[str]] = mapped_column(String(100))

    # dosages info
    dosages_fun_fact: Mapped[Optional[str]] = mapped_column(Text)

    is_danger: Mapped[bool] = mapped_column(Boolean, default=False, server_default="false", comment="опасный ли препарат (наркотик, стероид и т.д.)")

    # pharmacokinetics
    absorption: Mapped[Optional[str]] = mapped_column(String(100))
    metabolism: Mapped[Optional[str]] = mapped_column(Text)
    elimination: Mapped[Optional[str]] = mapped_column(Text)
    time_to_peak: Mapped[Optional[str]] = mapped_column(String(100))

    # pathways generation
    primary_action: Mapped[Optional[str]] = mapped_column(Text)
    secondary_actions: Mapped[Optional[str]] = mapped_column(Text)
    clinical_effects: Mapped[Optional[str]] = mapped_column(Text)

    pathways_sources: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String))
    dosages_sources: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String))

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
    )  # CHECK: Возможно, следует сделать lazy = ... чтобы не загружось все сразу

    analogs: Mapped[list["DrugAnalog"]] = relationship(
        back_populates="drug",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    prices: Mapped[list["DrugPrice"]] = relationship(
        back_populates="drug",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    researchs: Mapped[list["DrugResearch"]] = relationship(
        back_populates="drug",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    __table_args__ = (
        UniqueConstraint("id", "name"),
    )

    @property
    def schema_class(cls) -> Type[S]:
        return DrugSchema

    def get_schema(self) -> DrugSchema:
        return DrugSchema(
            id=self.id,
            name=self.name,
            latin_name=self.latin_name,
            name_ru=self.name_ru,
            description=self.description,
            classification=self.classification,
            dosages_fun_fact=self.dosages_fun_fact,

            is_danger=self.is_danger,

            synonyms=[syn.get_schema() for syn in self.synonyms] if self.synonyms else [],
            dosages=[dosage.get_schema() for dosage in self.dosages] if self.dosages else [],
            pathways=[pathway.get_schema() for pathway in self.pathways] if self.pathways else [],
            analogs=[analog.get_schema() for analog in self.analogs] if self.analogs else [],
            combinations=[comb.get_schema() for comb in self.combinations] if self.combinations else [],
            researches=[research.get_schema() for research in self.researchs] if self.researchs else [],

            drug_prices=[price.get_schema() for price in self.prices] if self.prices else None,

            pathways_sources=self.pathways_sources if self.pathways_sources else [],
            dosages_sources=self.dosages_sources if self.dosages_sources else [],

            primary_action=self.primary_action,
            secondary_actions=self.secondary_actions,
            clinical_effects=self.clinical_effects,

            created_at=self.created_at,
            updated_at=self.updated_at
        )


class DrugAnalog(IDMixin):
    __tablename__ = "drug_analogs"

    drug_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("drugs.id", ondelete="CASCADE", name="fk_drug_analogs_drug_id"),
        nullable=False,
        index=True
    )
    drug: Mapped["Drug"] = relationship(back_populates="analogs")

    analog_name: Mapped[str] = mapped_column(String(100), comment="аналог к основному drug")
    percent: Mapped[float] = mapped_column(Float, comment="процент схожести")
    difference: Mapped[str] = mapped_column(String(100), comment="отличие от основного препа")

    @property
    def schema_class(cls) -> Type[S]:
        return DrugAnalogResponse


class DrugSynonym(IDMixin):
    __tablename__ = "drug_synonyms"

    drug_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("drugs.id", ondelete="CASCADE", name="fk_drug_synonyms_drug_id"),
        nullable=False,
        index=True
    )
    drug: Mapped["Drug"] = relationship(back_populates="synonyms")

    synonym: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        comment="одно из названий препарата на русском"
    )

    __table_args__ = (
        UniqueConstraint("drug_id", "synonym", name="uq_drug_synonym"),

        # B-tree индекс для точного совпадения
        Index("idx_drug_synonyms_lower", func.lower(synonym), postgresql_using="btree"),

        # GIN индекс для нечеткого поиска (триграммы) регистронезависимого поиска (по умолчанию в trgm)
        Index(
            'trgm_drug_synonyms',
            synonym,
            postgresql_using='gin',
            postgresql_ops={'synonym': 'gin_trgm_ops'}
        )
    )

    @property
    def schema_class(cls) -> Type[S]:
        return DrugSynonymResponse


class DrugCombination(IDMixin):
    __tablename__ = "drug_combinations"

    drug_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("drugs.id", ondelete="CASCADE", name="fk_drug_combinations_drug_id"),
        nullable=False
    )
    drug: Mapped["Drug"] = relationship(back_populates="combinations")

    combination_type: Mapped[str] = mapped_column(String(10))  # 'good' или 'bad'
    substance: Mapped[str] = mapped_column(String(100))  # ДВ / ДВ или Класс для плохих комбинаций
    effect: Mapped[str] = mapped_column(Text)
    risks: Mapped[Optional[str]] = mapped_column(Text)  # Только для bad
    products: Mapped[Optional[list[str]]] = mapped_column(ARRAY(String))  # название препаратов с этим ДВ
    sources: Mapped[list[str]] = mapped_column(ARRAY(String))

    @property
    def schema_class(cls) -> Type[S]:
        return DrugCombinationResponse


class DrugPathway(IDMixin):
    __tablename__ = "drug_pathways"

    drug_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey('drugs.id', ondelete='CASCADE', name="fk_drug_pathways_drug_id"),
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
    note: Mapped[Optional[str]] = mapped_column(Text)  # Дополнительные примечания

    __table_args__ = (
        UniqueConstraint('drug_id', 'receptor', 'activation_type', name='uq_drug_pathway'),
    )

    @property
    def schema_class(cls) -> Type[S]:
        return DrugPathwayResponse


class DrugPrice(IDMixin, TimestampsMixin):
    __tablename__ = "drug_prices"

    drug_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey('drugs.id', ondelete='CASCADE', name="fk_drug_prices_drug_id"),
        nullable=False
    )
    drug: Mapped["Drug"] = relationship(back_populates="prices", )

    drug_brandname: Mapped[str] = mapped_column(String(100), unique=True)
    price: Mapped[float] = mapped_column(Float)
    shop_url: Mapped[str] = mapped_column(String(100))

    @property
    def schema_class(cls) -> ...:
        return ...


class DrugDosage(IDMixin):
    __tablename__ = 'drug_dosages'

    drug_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey('drugs.id', ondelete='CASCADE', name="fk_drug_dosages_drug_id"),
        nullable=False
    )
    drug: Mapped["Drug"] = relationship(back_populates="dosages")

    route: Mapped[Optional[str]] = mapped_column(
        String(30),
        comment="parental/topical/other"
    )
    method: Mapped[Optional[str]] = mapped_column(
        String(30),
        comment="intravenous/intramuscular/eye_drops/skin/nasal/peroral/inhalation/rectal/vaginal"
    )

    per_time: Mapped[Optional[str]] = mapped_column(String(100))
    max_day: Mapped[Optional[str]] = mapped_column(String(100))

    per_time_weight_based: Mapped[Optional[str]] = mapped_column(
        String(100),
        comment="for peroral and intramuscular only"
    )
    max_day_weight_based: Mapped[Optional[str]] = mapped_column(
        String(100),
        comment="for peroral and intramuscular only"
    )

    onset: Mapped[Optional[str]] = mapped_column(
        String(100),
        comment="<Время начала действия (например, 'немедленно'). Только для intramuscular/intravenous/peroral>"
    )
    half_life: Mapped[Optional[str]] = mapped_column(String(100), comment="период полувыведения")
    duration: Mapped[Optional[str]] = mapped_column(String(100), comment="продолжительность действия")

    notes: Mapped[Optional[str]] = mapped_column(String(100))

    __table_args__ = (
        UniqueConstraint('drug_id', 'route', 'method', name='uq_drug_dosage'),
    )

    @property
    def schema_class(cls) -> Type[S]:
        return DrugDosageResponse


class DrugResearch(IDMixin):
    __tablename__ = "drug_researchs"

    drug_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("drugs.id", ondelete="CASCADE", name="fk_drug_researchs_drug_id"),
        nullable=False,
        index=True
    )
    drug: Mapped["Drug"] = relationship(back_populates="researchs")

    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    publication_date: Mapped[date] = mapped_column(Date)
    url: Mapped[str] = mapped_column(String(255))
    summary: Mapped[Optional[str]] = mapped_column(Text)
    journal: Mapped[str] = mapped_column(String(100))
    doi: Mapped[str] = mapped_column(String(100), unique=True)
    authors: Mapped[Optional[str]] = mapped_column(Text)
    study_type: Mapped[Optional[str]] = mapped_column(String(150))
    interest: Mapped[float] = mapped_column()

    __table_args__ = (
        Index('idx_drug_researchs_doi', doi, unique=True),
    )

    @property
    def schema_class(cls) -> Type[S]:
        return DrugResearchResponse
