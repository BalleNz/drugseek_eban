import uuid
from datetime import datetime

from sqlalchemy import String, ForeignKey, Text, Boolean, Index, Table, Column
from sqlalchemy import func, DateTime
from sqlalchemy import insert
from sqlalchemy.dialects.postgresql import UUID as PG_UUID  # Важно импортировать UUID для PostgreSQL
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database.models.base import IDMixin, TimestampsMixin
from database.models.drug import Drug

users_allowed_drugs = Table(
    "users_allowed_drugs",
    IDMixin.metadata,
    Column("user_id", PG_UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
    Column("drug_id", PG_UUID(as_uuid=True), ForeignKey("drugs.id", ondelete="CASCADE"), primary_key=True)
)


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

    allowed_drugs: Mapped[list["Drug"]] = relationship(
        secondary="users_allowed_drugs",  # имя таблицы связи
        lazy="selectin"
    )

    __table_args__ = (
        Index('uq_users_telegram_id', 'telegram_id', unique=True),
        Index('uq_users_username', 'username', unique=True),
    )

    async def add_allowed_drug_by_id(
            self,
            drug_id: uuid.UUID,
            session: AsyncSession
    ) -> "User":
        """Добавляет препарат в разрешенные по его ID без загрузки объекта"""
        stmt = insert(users_allowed_drugs).values(
            user_id=self.id,
            drug_id=drug_id
        ).on_conflict_do_nothing()

        await session.execute(stmt)
        await session.commit()
        return self


class UserRequestLog(IDMixin):
    """Логирование исрасходованных запросов пользователя"""
    __tablename__ = "user_request_logs"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    user_query: Mapped[str] = mapped_column(String, comment="запрос пользователя")
    used_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
