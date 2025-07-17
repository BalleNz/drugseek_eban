import uuid
from datetime import datetime
from sqlalchemy import func, DateTime

from database.models.base import IDMixin, TimestampsMixin
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, ForeignKey, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID as PG_UUID  # Важно импортировать UUID для PostgreSQL


class User(IDMixin, TimestampsMixin):
    __tablename__ = "users"

    telegram_id: Mapped[str] = mapped_column(String, comment="telegram id")
    username: Mapped[str] = mapped_column(String, comment="telegram username")
    first_name: Mapped[str] = mapped_column(String, comment="telegram first name")
    last_name: Mapped[str] = mapped_column(String, comment="telegram last name")
    is_premium: Mapped[bool] = mapped_column(Boolean, comment="has premium on telegram account?")

    allowed_requests: Mapped[int] = mapped_column(default=3, comment="Количество разрешенных запросов")
    used_requests: Mapped[int] = mapped_column(default=0, comment="Количество использованных запросов")

    # TODO: prompt + if not used_requests % 10: user_service.user_desrciption_update(user)
    description: Mapped[str] = mapped_column(
        Text,
        comment="Каждые 10 запросов о пользователе обновляется его описание. Аля 'какой ты биофакер/химик/фармацевт?'"
    )

    allowed_drugs: Mapped[list["UserDrugs"]] = relationship(
        back_populates="user"
    )


class UserDrugs(IDMixin):
    __tablename__ = "users_allowed_drugs"

    drug_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("drugs.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )

    user_id: Mapped[uuid.UUID] = mapped_column(
        PG_UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True
    )
    user: Mapped[User] = relationship(back_populates="allowed_drugs")


class UserRequestLog(IDMixin):
    """Логирование исрасходованных запросов пользователя"""
    __tablename__ = "user_request_logs"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    user_query: Mapped[str] = mapped_column(String, comment="запрос пользователя")
    used_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
