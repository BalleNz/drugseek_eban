import uuid
from datetime import datetime
from typing import Optional

from sqlalchemy import String, ForeignKey, Text, Index, func, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship

from drug_search.core.database.models.base import IDMixin, TimestampsMixin


class User(IDMixin, TimestampsMixin):
    __tablename__ = "users"

    telegram_id: Mapped[str] = mapped_column(String, comment="telegram id")
    username: Mapped[str] = mapped_column(String, comment="telegram username")
    first_name: Mapped[Optional[str]] = mapped_column(String, comment="telegram first name")
    last_name: Mapped[Optional[str]] = mapped_column(String, comment="telegram last name")

    allowed_requests: Mapped[int] = mapped_column(default=3, comment="Количество разрешенных запросов")
    used_requests: Mapped[int] = mapped_column(default=0, comment="Количество использованных запросов")

    # TODO: prompt + if not used_requests % 10: user_service.user_description_update(user)
    description: Mapped[Optional[str]] = mapped_column(
        Text,
        default=None,
        comment="Каждые 10 запросов о пользователе обновляется его описание. Аля 'какой ты биофакер/химик/фармацевт?'"
    )

    allowed_drugs: Mapped[list["AllowedDrugs"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        lazy="selectin"
    )

    @property
    def allowed_drug_ids(self) -> list[uuid.UUID]:
        return [ad.drug_id for ad in self.allowed_drugs]

    __table_args__ = (
        Index('uq_users_telegram_id', 'telegram_id', unique=True),
        Index('uq_users_username', 'username', unique=True),
    )


class UserRequestLog(IDMixin):
    """Логирование исрасходованных запросов пользователя"""
    __tablename__ = "user_request_logs"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    user_query: Mapped[str] = mapped_column(String, comment="запрос пользователя")
    used_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
