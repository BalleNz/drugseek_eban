import uuid
from typing import Type

from sqlalchemy import String, Integer, UUID as PG_UUID, ForeignKey
from sqlalchemy.orm import mapped_column, Mapped, relationship

from drug_search.core.schemas.payment_schema import PaymentSchema
from drug_search.infrastructure.database.models.base import IDMixin, TimestampsMixin, S


class Payment(IDMixin, TimestampsMixin):
    __tablename__ = "payment_logs"

    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE")
    )

    package_key: Mapped[str] = mapped_column(String(100), comment="Ключ платежа (пакета)")
    payment_name: Mapped[str] = mapped_column(String(100), comment="Название платежа")
    price: Mapped[int] = mapped_column(Integer, comment="Сумма платежа в рублях")

    user: Mapped["User"] = relationship(back_populates="payment_logs")

    @property
    def schema_class(cls) -> Type[S]:
        return PaymentSchema
