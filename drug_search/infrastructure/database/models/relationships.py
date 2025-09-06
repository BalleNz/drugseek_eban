import uuid
from typing import Type

from sqlalchemy import ForeignKey, Index
from sqlalchemy.dialects.postgresql import UUID as PG_UUID  # Важно импортировать UUID для PostgreSQL
from sqlalchemy.orm import Mapped, mapped_column, relationship

from drug_search.infrastructure.database.models.base import S
from drug_search.infrastructure.database.models.base import IDMixin
from drug_search.core.schemas.user_schemas import AllowedDrugSchema


class AllowedDrugs(IDMixin):
    __tablename__ = "allowed_drugs"

    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True
    )
    drug_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("drugs.id", ondelete="CASCADE", use_alter=True),
        primary_key=True
    )

    user: Mapped["User"] = relationship(back_populates="allowed_drugs", lazy="selectin")
    drug: Mapped["Drug"] = relationship(lazy="selectin")

    __table_args__ = (
        Index('ix_allowed_drugs_user_id_drug_id', 'user_id', 'drug_id'),
    )

    def schema_class(cls) -> Type[S]:
        return AllowedDrugSchema
