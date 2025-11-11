import uuid
from datetime import date
from typing import Optional, Type, TypeVar, Generic

from pydantic import BaseModel
from sqlalchemy import String, Float, ForeignKey, Text, UniqueConstraint, ARRAY, Index, func, Date, JSON, TypeDecorator
from sqlalchemy.dialects.postgresql import UUID as PG_UUID  # Важно импортировать UUID для PostgreSQL
from sqlalchemy.orm import Mapped, mapped_column, relationship

from drug_search.core.schemas import DrugAnalogSchema, DrugCombinationSchema, DrugPathwaySchema, \
    DrugResearchSchema, DrugSynonymSchema, DrugDosageSchema, DrugSchema, Pharmacokinetics, MetabolismPhase, \
    EliminationInfo
from drug_search.infrastructure.database.models.base import TimestampsMixin, IDMixin
from drug_search.infrastructure.database.models.types import DangerClassificationEnum

M = TypeVar("M", bound=IDMixin)
S = TypeVar("S", bound=BaseModel)


class PydanticTypeList(TypeDecorator, Generic[S]):
    impl = JSON
    cache_ok = True

    def __init__(self, pydantic_type: Type[S], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.pydantic_type = pydantic_type

    def process_bind_param(self, value: list[S] | None, dialect):
        if value is None:
            return None
        return [item.model_dump() for item in value]

    def process_result_value(self, value: list | None, dialect):
        if value is None:
            return None
        return [self.pydantic_type(**item) for item in value]


class Drug(IDMixin, TimestampsMixin):
    __tablename__ = "drugs"

    name: Mapped[str] = mapped_column(String(100), unique=True)  # ДВ на англ
    name_ru: Mapped[Optional[str]] = mapped_column(String(100))  # ДВ на русском
    latin_name: Mapped[Optional[str]] = mapped_column(String(100))

    # [ briefly info ]
    description: Mapped[Optional[str]] = mapped_column(Text)
    classification: Mapped[Optional[str]] = mapped_column(Text)
    fact: Mapped[Optional[str]] = mapped_column(Text)

    # следующие поля не выношу в отдельные таблицы, это негативно влияет на производительность в моем случае
    # [ analogs ]
    analogs_description: Mapped[Optional[str]] = mapped_column(Text)

    # [ dosages info ]
    fun_facts: Mapped[list[str] | None] = mapped_column(ARRAY(Text))

    danger_classification: Mapped[DangerClassificationEnum] = mapped_column(
        DangerClassificationEnum,
        comment="классификация опасности препарата: "
                "SAFE - безопасен"
                "PREMIUM_NEED - сомнительно"
                "DANGER - запрещен в рф"
    )

    # [ pharmacokinetics ]
    pharmacokinetics: Mapped[list[Pharmacokinetics] | None] = mapped_column(
        PydanticTypeList(Pharmacokinetics),
        comment="JSON список фармакокинетики"
    )
    metabolism: Mapped[list[MetabolismPhase] | None] = mapped_column(
        PydanticTypeList(MetabolismPhase),
        comment="JSON список фаз метаболизма {phase, process, result}"
    )
    elimination: Mapped[list[EliminationInfo] | None] = mapped_column(
        PydanticTypeList(EliminationInfo),
        comment="JSON список выведения {excrement_type, output_percent}"
    )
    metabolism_description: Mapped[Optional[str]] = mapped_column(Text)

    # [ pathways ]
    primary_action: Mapped[Optional[str]] = mapped_column(Text)
    secondary_actions: Mapped[Optional[str]] = mapped_column(Text)
    clinical_effects: Mapped[Optional[str]] = mapped_column(Text)

    # [ sources ]
    pathways_sources: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text))
    dosage_sources: Mapped[Optional[list[str]]] = mapped_column(ARRAY(Text))

    # [ relationships ]
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
    )  # CHECK: Возможно, следует сделать lazy = ... чтобы не загружалось все сразу

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

    researches: Mapped[list["DrugResearch"]] = relationship(
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
        def _map_schemas(items):
            return [item_schema for item in items if (item_schema := item.get_schema())] if items else []

        return DrugSchema(
            id=self.id,
            name=self.name,
            latin_name=self.latin_name,
            name_ru=self.name_ru,
            description=self.description,
            classification=self.classification,
            fun_facts=self.fun_facts,

            fact=self.fact,
            analogs_description=self.analogs_description,
            metabolism_description=self.metabolism_description,

            pharmacokinetics=self.pharmacokinetics or [],
            metabolism=self.metabolism or [],
            elimination=self.elimination or [],

            danger_classification=self.danger_classification,

            synonyms=_map_schemas(self.synonyms),
            dosages=_map_schemas(self.dosages),
            pathways=_map_schemas(self.pathways),
            analogs=_map_schemas(self.analogs),
            combinations=_map_schemas(self.combinations),
            researches=_map_schemas(self.researches),

            prices=None,

            pathways_sources=self.pathways_sources if self.pathways_sources else [],
            dosage_sources=self.dosage_sources if self.dosage_sources else [],

            primary_action=self.primary_action,
            secondary_actions=self.secondary_actions,
            clinical_effects=self.clinical_effects,

            created_at=self.created_at,
            updated_at=self.updated_at
        )  # TODO сделать в базовой модели


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
    percent: Mapped[float] = mapped_column(String(10), comment="процент схожести")
    difference: Mapped[str] = mapped_column(Text, comment="отличие от основного препа")

    @property
    def schema_class(cls) -> Type[S]:
        return DrugAnalogSchema


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
        unique=False,
        comment="одно из названий препарата на русском"
    )

    __table_args__ = (
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
        return DrugSynonymSchema


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

    @property
    def schema_class(cls) -> Type[S]:
        return DrugCombinationSchema


class DrugPathway(IDMixin):
    __tablename__ = "drug_pathways"

    drug_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey('drugs.id', ondelete='CASCADE', name="fk_drug_pathways_drug_id"),
        nullable=False
    )
    drug: Mapped["Drug"] = relationship(back_populates="pathways")

    receptor: Mapped[str] = mapped_column(String(100), nullable=False, comment="название рецептора")
    binding_affinity: Mapped[Optional[str]] = mapped_column(String(200), comment="сила связывания")
    affinity_description: Mapped[Optional[str]] = mapped_column(String(200), comment="сила связывания")
    activation_type: Mapped[str] = mapped_column(String(200), nullable=False, comment="тип активации")
    pathway: Mapped[Optional[str]] = mapped_column(String(200), comment="сигнальный путь")
    effect: Mapped[Optional[str]] = mapped_column(String(200), comment="физиологический эффект")

    note: Mapped[Optional[str]] = mapped_column(Text, comment="дополнительные примечания")

    @property
    def schema_class(cls) -> Type[S]:
        return DrugPathwaySchema


class DrugPrice(IDMixin, TimestampsMixin):
    __tablename__ = "drug_prices"

    drug_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey('drugs.id', ondelete='CASCADE', name="fk_drug_prices_drug_id"),
        nullable=False
    )
    drug: Mapped["Drug"] = relationship(back_populates="prices", )

    drug_brand: Mapped[str] = mapped_column(String(100), unique=True)
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
        String(50),
        comment="parental/topical/other"
    )
    method: Mapped[Optional[str]] = mapped_column(
        String(50),
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

    notes: Mapped[Optional[str]] = mapped_column(Text)

    __table_args__ = (
        UniqueConstraint('drug_id', 'route', 'method', name='uq_drug_dosage'),
    )

    @property
    def schema_class(cls) -> Type[S]:
        return DrugDosageSchema


class DrugResearch(IDMixin):
    __tablename__ = "drug_researchs"

    drug_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("drugs.id", ondelete="CASCADE", name="fk_drug_researches_drug_id"),
        nullable=False,
        index=True
    )
    drug: Mapped["Drug"] = relationship(back_populates="researches")

    name: Mapped[str] = mapped_column(String(255))
    description: Mapped[str] = mapped_column(Text)
    publication_date: Mapped[date] = mapped_column(Date)
    url: Mapped[str] = mapped_column(String(255))
    summary: Mapped[Optional[str]] = mapped_column(Text)
    journal: Mapped[str] = mapped_column(String(255))
    doi: Mapped[str] = mapped_column(String(100), unique=True)
    authors: Mapped[Optional[str]] = mapped_column(Text)
    study_type: Mapped[Optional[str]] = mapped_column(String(150))
    interest: Mapped[float] = mapped_column()

    __table_args__ = (
        Index('idx_drug_researches_doi', doi, unique=True),
    )

    @property
    def schema_class(cls) -> Type[S]:
        return DrugResearchSchema
