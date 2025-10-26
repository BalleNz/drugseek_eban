import uuid
from datetime import datetime
from typing import Optional, Type, TypeVar, Union

from pydantic import BaseModel
from sqlalchemy import String, ForeignKey, Text, Index, func, DateTime, Integer, UUID as PG_UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from drug_search.core.lexicon import SUBSCRIBE_TYPES, DEFAULT_SEARCH_DAY_LIMIT, ASSISTANT_TOKENS_START
from drug_search.core.schemas import UserSchema, UserRequestLogSchema, AllowedDrugSchema
from drug_search.infrastructure.database.models.base import IDMixin, TimestampsMixin
from drug_search.infrastructure.database.models.types import UserSubscriptionTypes

M = TypeVar("M", bound='IDMixin')
S = TypeVar("S", bound=BaseModel)


class User(IDMixin, TimestampsMixin):
    __tablename__ = "users"

    telegram_id: Mapped[str] = mapped_column(String, comment="telegram id")
    username: Mapped[str] = mapped_column(String, comment="telegram username")
    first_name: Mapped[Optional[str]] = mapped_column(String, comment="telegram first name")
    last_name: Mapped[Optional[str]] = mapped_column(String, comment="telegram last name")

    # subscription
    subscription_type: Mapped[UserSubscriptionTypes] = mapped_column(
        UserSubscriptionTypes,
        server_default=SUBSCRIBE_TYPES.DEFAULT.value,
        default=SUBSCRIBE_TYPES.DEFAULT,
        comment="Тип подписки юзера"
    )
    subscription_end: Mapped[Optional[datetime]] = mapped_column(DateTime, comment="Конец подписки")

    allowed_search_requests: Mapped[int] = mapped_column(
        Integer,
        default=DEFAULT_SEARCH_DAY_LIMIT,
        server_default=f"{DEFAULT_SEARCH_DAY_LIMIT}",
        comment="Оставшиеся запросы на поиск препов"
    )
    allowed_question_requests: Mapped[int] = mapped_column(
        Integer,
        default=ASSISTANT_TOKENS_START,
        server_default=f"{ASSISTANT_TOKENS_START}",
        comment="Оставшиеся запросы на вопросы"
    )

    used_requests: Mapped[int] = mapped_column(Integer, default=0, comment="Количество использованных запросов в общем")
    requests_last_refresh: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        server_default=func.now(),
        comment="последний сброс счётчика"
    )

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

    def get_schema(self) -> Union[S, list[None]]:
        return UserSchema(
            id=self.id,
            telegram_id=self.telegram_id,
            username=self.username,
            first_name=self.first_name,
            last_name=self.last_name,
            subscription_type=self.subscription_type,
            subscription_end=self.subscription_end,
            allowed_search_requests=self.allowed_search_requests,
            allowed_question_requests=self.allowed_question_requests,
            used_requests=self.used_requests,
            requests_last_refresh=self.requests_last_refresh,
            description=self.description,
            allowed_drugs=[al for al in self.allowed_drugs],
            created_at=self.created_at,
            updated_at=self.updated_at
        )

    __table_args__ = (
        Index('uq_users_telegram_id', 'telegram_id', unique=True),
    )

    @property
    def schema_class(cls) -> Type[S]:
        return UserSchema


class UserRequestLog(IDMixin):
    """Логирование израсходованных запросов пользователя"""
    __tablename__ = "user_request_logs"

    user_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id"))
    user_query: Mapped[str] = mapped_column(String, comment="запрос пользователя")
    used_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    @property
    def schema_class(cls) -> Type[S]:
        return UserRequestLogSchema


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

    @property
    def schema_class(cls) -> Type[S]:
        return AllowedDrugSchema
