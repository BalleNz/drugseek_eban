from enum import Enum
from typing import Optional
from uuid import UUID

from redis.asyncio import Redis

from drug_search.config import config
from drug_search.core.schemas import DrugSchema, AllowedDrugsSchema, UserSchema


class CacheKeys(str, Enum):
    ALLOWED_DRUGS = "allowed_drugs_info"
    DRUG = "drug"
    USER_PROFILE = "user_profile"


class RedisService:
    def __init__(self, redis_client: Redis):
        self.redis = redis_client

    @staticmethod
    def _get_token_key(telegram_id: str) -> str:
        return f"auth_{telegram_id}"

    @staticmethod
    def _get_allowed_drugs_key(telegram_id: str) -> str:
        return f"user:{telegram_id}:{CacheKeys.ALLOWED_DRUGS}"

    @staticmethod
    def _get_drug_key(drug_id: UUID) -> str:
        return f"{CacheKeys.DRUG}:{drug_id}"

    @staticmethod
    def _get_user_profile_key(telegram_id: str):
        return f"user:{telegram_id}:{CacheKeys.USER_PROFILE}"

    async def get_access_token(self, telegram_id: str) -> Optional[str]:
        """Получение access token из кэша"""
        redis_key = self._get_token_key(telegram_id)
        return await self.redis.get(redis_key)

    async def set_access_token(
        self,
        telegram_id: str,
        access_token: str,
        expire_seconds: int = config.ACCESS_TOKEN_EXPIRES_MINUTES
    ) -> None:
        """Сохранение access token в кэш"""
        redis_key = self._get_token_key(telegram_id)
        await self.redis.set(redis_key, access_token, ex=expire_seconds)

    async def get_allowed_drugs(self, telegram_id: str) -> Optional[AllowedDrugsSchema]:
        """Получение списка разрешенных лекарств из кэша"""
        cache_key = self._get_allowed_drugs_key(telegram_id)
        cached_data = await self.redis.get(cache_key)
        if cached_data:
            return AllowedDrugsSchema.model_validate_json(cached_data)
        return None

    async def set_allowed_drugs(
        self,
        telegram_id: str,
        data: AllowedDrugsSchema,
        expire_seconds: int = 86400
    ) -> None:
        """Сохранение списка разрешенных лекарств в кэш"""
        cache_key = self._get_allowed_drugs_key(telegram_id)
        await self.redis.set(
            cache_key,
            data.model_dump_json(),
            ex=expire_seconds
        )

    async def get_drug(self, drug_id: UUID) -> Optional[DrugSchema]:
        """Получение информации о лекарстве из кэша"""
        cache_key = self._get_drug_key(drug_id)
        cached_data = await self.redis.get(cache_key)
        if cached_data:
            return DrugSchema.model_validate_json(cached_data)
        return None

    async def set_drug(
        self,
        drug_id: UUID,
        data: DrugSchema,
        expire_seconds: int = 86400
    ) -> None:
        """Сохранение информации о лекарстве в кэш"""
        cache_key = self._get_drug_key(drug_id)
        await self.redis.set(
            cache_key,
            data.model_dump_json(),
            ex=expire_seconds
        )

    async def get_user_profile(
            self,
            telegram_id: str
    ) -> Optional[UserSchema]:
        """Получение юзера"""
        cache_key = self._get_user_profile_key(telegram_id)
        cache_data: Optional[str] = await self.redis.get(
            cache_key
        )
        if cache_data:
            return UserSchema.model_validate_json(cache_data)
        return None

    async def set_user_profile(
            self,
            telegram_id: str,
            data: UserSchema,
            expire_seconds: int = 86400
    ):
        """Сохранение информации о профиле юзера"""
        cache_key: str = self._get_user_profile_key(telegram_id)
        await self.redis.set(
            cache_key,
            data.model_dump_json(),
            ex=expire_seconds
        )

    async def invalidate_allowed_drugs(self, telegram_id: str) -> None:
        """Инвалидация кэша списка лекарств"""
        cache_key: str = self._get_allowed_drugs_key(telegram_id)
        await self.redis.delete(cache_key)

    async def invalidate_drug_describe(self, telegram_id: str, drug_id: UUID) -> None:
        """Инвалидация кэша информации о лекарстве"""
        cache_key: str = self._get_drug_key(telegram_id, drug_id)
        await self.redis.delete(cache_key)

    async def invalidate_user_profile(self, telegram_id: str) -> None:
        """Инвалидация кэша профиля юзера"""
        cache_key: str = self._get_user_profile_key(telegram_id)
        await self.redis.delete(cache_key)
